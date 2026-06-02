"""
Fashion Futures Market — Scraper Pipeline
==========================================
Two-step scoring architecture:
  Step 1: Deterministic formula (scoring/formula.py) → produces the number
  Step 2: Claude narrative (ai/trend_scorer.py)      → produces the words

No LLM-generated numbers enter the database.
Every score is traceable to real signal data.

Usage:
    python -m scrapers.pipeline
"""
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from dotenv import load_dotenv
load_dotenv(_BACKEND_DIR / ".env", override=True)

from scrapers import trendhunter_scraper, google_trends_scraper, reddit_scraper, tiktok_scraper, pinterest_scraper
from scoring.formula import (
    TrendSignalData, compute_score,
    score_from_pinterest_row, score_from_google_trends,
    ScoreResult,
)
from ai.trend_scorer import generate_narrative
from db.models import Trend, Market, TrendStatus, MarketStatus, TrendScoreHistory
from db.session import SessionLocal


# ── Deduplication ─────────────────────────────────────────────────────────────

def _normalise(text: str) -> str:
    return " ".join(text.lower().split())

def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    return len(a & b) / len(union) if union else 0.0

def _token_set(text: str) -> set[str]:
    stop = {"a","an","the","is","in","on","at","for","to","of","and","or","with"}
    return {w for w in _normalise(text).split() if w not in stop and len(w) > 2}

def deduplicate(signals: list[dict], threshold: float = 0.45) -> list[dict]:
    unique: list[dict] = []
    for sig in signals:
        title = sig.get("title") or sig.get("term") or ""
        tokens = _token_set(title)
        is_dup = any(
            _jaccard(tokens, _token_set(k.get("title") or k.get("term") or "")) >= threshold
            for k in unique
        )
        if not is_dup:
            unique.append(sig)
    return unique


# ── Signal → ScoreResult ──────────────────────────────────────────────────────

def _compute_signal_score(signal: dict) -> ScoreResult:
    """
    Route each signal to the appropriate scoring wrapper based on source.
    All paths produce a ScoreResult with real computed components.
    """
    source = signal.get("source", "unknown")

    if source == "google_trends":
        return score_from_google_trends(
            trend_name    = signal.get("term") or signal.get("title", ""),
            weekly_volumes= signal.get("weekly_volumes", []),
            velocity_pct  = float(signal.get("velocity_score", 0)),
            also_on_reddit= bool(signal.get("reddit_confirmed", False)),
        )

    if source == "pinterest" and "term" in signal:
        # Pinterest scraper signals have 'term' key and full growth_rates data
        return score_from_pinterest_row(
            trend_name         = signal.get("term", ""),
            normalized_volume  = float(signal.get("normalized_volume", 50)),
            weekly_change_pct  = float(signal.get("wow_change_pct") or 0),
            monthly_change_pct = float(signal.get("mom_change_pct") or 0),
            yoy_change_pct     = float(signal.get("yoy_change_pct") or 0),
            weekly_volumes     = signal.get("weekly_volumes", []),
            also_on_google     = bool(signal.get("google_confirmed", False)),
            also_on_reddit     = bool(signal.get("reddit_confirmed", False)),
        )

    if source == "pinterest":
        return score_from_pinterest_row(
            trend_name         = signal.get("title", ""),
            normalized_volume  = float(signal.get("normalized_volume", 50)),
            weekly_change_pct  = float(signal.get("weekly_change_pct", 0)),
            monthly_change_pct = float(signal.get("monthly_change_pct", 0)),
            yoy_change_pct     = float(signal.get("yoy_change_pct", 0)),
            weekly_volumes     = signal.get("weekly_volumes", []),
            also_on_google     = bool(signal.get("google_confirmed", False)),
            also_on_reddit     = bool(signal.get("reddit_confirmed", False)),
        )

    if source == "tiktok":
        wow = float(signal.get("tiktok_growth_pct") or signal.get("effective_wow", 0))
        data = TrendSignalData(
            trend_name         = signal.get("title", ""),
            monthly_change_pct = wow,   # best monthly proxy we have
            tiktok_growth_pct  = wow,
        )
        return compute_score(data)

    if source == "reddit":
        # Reddit posts don't have search-volume data — use cross-platform
        # presence as the primary signal, velocity from upvote score
        upvote_score = float(signal.get("score", 0))
        # Normalize upvote score: 1000 upvotes ≈ velocity 50%
        velocity_proxy = min(200.0, upvote_score / 20)
        data = TrendSignalData(
            trend_name         = signal.get("title", ""),
            monthly_change_pct = velocity_proxy,
            normalized_volume  = min(100, upvote_score / 10),
            on_reddit          = upvote_score,
        )
        return compute_score(data)

    # Editorial RSS — no numeric data but headline language carries signal strength
    if source == "editorial_rss":
        title = signal.get("title", "").lower()
        # Strong editorial language → treat as ~30% monthly velocity proxy
        if any(w in title for w in ["comeback", "revival", "is back", "making a return",
                                     "the new ", "replace", "everyone is", "everywhere"]):
            velocity_proxy = 40.0
        elif any(w in title for w in ["trend", "trending", "moment", "rising", "taking off",
                                       "summer 2026", "spring 2026", "best ", "top "]):
            velocity_proxy = 20.0
        else:
            velocity_proxy = 10.0
        data = TrendSignalData(
            trend_name         = signal.get("title", ""),
            monthly_change_pct = velocity_proxy,
        )
        return compute_score(data)

    # Generic fallback — limited numeric data, fall back to neutral on missing fields
    data = TrendSignalData(
        trend_name         = signal.get("title", ""),
        monthly_change_pct = float(signal.get("velocity_score", 0)) or None,
        on_pinterest       = False,
        on_google_trends   = False,
        on_reddit          = False,
    )
    return compute_score(data)


# ── Signal normalisation ──────────────────────────────────────────────────────

def _normalise_signal(raw: dict) -> dict:
    signal: dict = {"source": raw.get("source", "unknown")}
    if "term" in raw:
        signal["title"]         = raw["term"]
        signal["description"]   = (
            f"Rising search term. Velocity: {raw.get('velocity_score', 0):.1f}%. "
            f"Related: {', '.join(raw.get('rising_queries', []))}"
        )
        signal["velocity_score"]  = raw.get("velocity_score", 0.0)
        signal["weekly_volumes"]  = raw.get("weekly_volumes", [])
        signal["keywords"]        = raw.get("rising_queries", [])
    elif raw.get("source") == "tiktok":
        # TikTok signals carry their own structured data — pass through intact
        signal.update(raw)
    else:
        signal["title"]           = raw.get("title", "")
        signal["description"]     = raw.get("description", "")
        signal["url"]             = raw.get("url", "")
        signal["keywords"]        = raw.get("keywords", [])
        signal["velocity_score"]  = 0.0
        signal["score"]           = raw.get("score", 0)   # reddit upvotes
    return signal


# ── DB write ──────────────────────────────────────────────────────────────────

def _similar_name(a: str, b: str) -> bool:
    """True if two trend names are close enough to be the same trend."""
    stop = {"aesthetic", "revival", "fashion", "style", "the", "of", "and", "a", "an"}
    def tokens(s):
        import re
        s = re.sub(r"^#", "", s.lower())
        return {w for w in re.sub(r"[^\w\s]", "", s).split() if w not in stop and len(w) > 3}
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return a.lower().strip() == b.lower().strip()
    shared = ta & tb
    smaller = min(len(ta), len(tb))
    return len(shared) >= 2 or (smaller > 0 and len(shared) / smaller >= 0.6)


def _find_existing(db, name: str, source: str) -> Trend | None:
    """
    Check if a trend with this name already exists in the DB.
    Checks exact name match first, then fuzzy match within same source.
    """
    # Exact match (case-insensitive)
    exact = db.query(Trend).filter(
        Trend.name.ilike(name)
    ).first()
    if exact:
        return exact

    # Fuzzy match — same source, similar name
    same_source = db.query(Trend).filter(Trend.source == source).all()
    for t in same_source:
        if _similar_name(t.name, name):
            return t
    return None


def _snapshot_score(db, trend: Trend, now: datetime):
    """Record a score history entry for sparkline display."""
    snap = TrendScoreHistory(
        id          = str(uuid.uuid4()),
        trend_id    = trend.id,
        score       = trend.ai_score,
        velocity    = trend.signal_velocity or 0.0,
        recorded_at = now.replace(tzinfo=None),
    )
    db.add(snap)


def _write_trend_and_market(
    db,
    signal: dict,
    score_result: ScoreResult,
    narrative: dict,
) -> tuple[Trend, Market, str]:
    """
    Upsert-aware writer.
    - If trend already exists: update score, velocity, thesis, snapshot history
    - If new: insert trend + open market
    Returns (trend, market, action) where action is 'created' or 'updated'.
    """
    now             = datetime.now(tz=timezone.utc)
    trend_name      = narrative.get("trend_name") or signal.get("title", "Unknown")
    source          = signal.get("source", "unknown")
    new_score       = score_result.score
    new_velocity    = score_result.components.get("velocity", 0.0)

    # ── Check if trend already exists ────────────────────────────────────────
    existing = _find_existing(db, trend_name, source)

    if existing:
        # Update score only if it changed meaningfully (±0.2)
        score_changed = abs((existing.ai_score or 0) - new_score) >= 0.2
        if score_changed:
            existing.ai_score        = new_score
            existing.signal_velocity = new_velocity
            existing.score_updated_at = now.replace(tzinfo=None)
            # Keep best thesis (update if score improved)
            if new_score > (existing.ai_score or 0):
                existing.ai_thesis   = narrative.get("thesis", existing.ai_thesis)
                existing.description = narrative.get("thesis", existing.description)
            _snapshot_score(db, existing, now)

        # Reopen market if it was closed and score is strong again
        existing_market = next((m for m in existing.markets if m.status == MarketStatus.open), None)
        if not existing_market:
            # Open a fresh market with new resolution date
            question = (
                narrative.get("resolution_question")
                or f"Will '{existing.name}' reach mainstream adoption within 90 days?"
            )
            new_market = Market(
                id                  = str(uuid.uuid4()),
                trend_id            = existing.id,
                question            = question,
                resolution_date     = (now + timedelta(days=90)).replace(tzinfo=None),
                resolution_criteria = question,
                yes_price           = 0.5,
                no_price            = 0.5,
                liquidity_param     = 100.0,
                total_volume        = 0,
                status              = MarketStatus.open,
                created_at          = now.replace(tzinfo=None),
            )
            db.add(new_market)
            return existing, new_market, "updated+reopened"

        return existing, existing_market, "updated"

    # ── New trend — full insert ────────────────────────────────────────────────
    trend_id  = str(uuid.uuid4())
    market_id = str(uuid.uuid4())

    trend = Trend(
        id               = trend_id,
        name             = trend_name,
        description      = narrative.get("thesis", ""),
        ai_score         = new_score,
        ai_thesis        = narrative.get("thesis", ""),
        source           = source,
        signal_velocity  = new_velocity,
        status           = TrendStatus.emerging,
        created_at       = now.replace(tzinfo=None),
        score_updated_at = now.replace(tzinfo=None),
    )

    question = (
        narrative.get("resolution_question")
        or f"Will '{trend.name}' reach mainstream adoption within 90 days?"
    )

    market = Market(
        id                   = market_id,
        trend_id             = trend_id,
        question             = question,
        resolution_date      = (now + timedelta(days=90)).replace(tzinfo=None),
        resolution_criteria  = question,
        yes_price            = 0.5,
        no_price             = 0.5,
        liquidity_param      = 100.0,
        total_volume         = 0,
        status               = MarketStatus.open,
        created_at           = now.replace(tzinfo=None),
    )

    db.add(trend)
    db.add(market)
    _snapshot_score(db, trend, now)
    return trend, market, "created"


# ── Main pipeline ─────────────────────────────────────────────────────────────

def run_pipeline() -> None:
    print("=" * 60)
    print("Fashion Futures Market — Scraper Pipeline")
    print("Two-step: formula scoring → Claude narrative")
    print("=" * 60)

    # 1. Scrape
    print("\n[1/5] Running scrapers...")
    raw_signals: list[dict] = []
    for name, fn in [
        ("Editorial RSS",  lambda: trendhunter_scraper.scrape()),
        ("Google Trends",  lambda: google_trends_scraper.scrape()),
        ("Reddit",         lambda: reddit_scraper.run_reddit_scrape()),
        ("TikTok",         lambda: tiktok_scraper.scrape()),
        ("Pinterest",      lambda: pinterest_scraper.scrape()),
    ]:
        try:
            print(f"  → {name}...")
            results = fn()
            raw_signals.extend(results)
            print(f"     {len(results)} signals")
        except Exception as e:
            print(f"  [WARN] {name} failed: {e}")

    print(f"  Total raw: {len(raw_signals)}")

    # 2. Normalise + deduplicate
    print("\n[2/5] Deduplicating...")
    normalised     = [_normalise_signal(s) for s in raw_signals]
    unique_signals = deduplicate(normalised)
    print(f"  Unique signals: {len(unique_signals)}")

    # 3. Formula scoring (no Claude, pure math)
    print("\n[3/5] Formula scoring (deterministic)...")
    scored_signals: list[tuple[dict, ScoreResult]] = []
    for signal in unique_signals:
        try:
            result = _compute_signal_score(signal)
            scored_signals.append((signal, result))
            title = signal.get("title") or signal.get("term") or "?"
            print(f"  {result.score:4.1f}/10  [{result.data_completeness:.0%} data]  {title[:55]}")
        except Exception as e:
            print(f"  [WARN] Scoring failed: {e}")

    # 4. Filter low scores before spending API calls on Claude
    # Source-aware thresholds:
    #   Data-backed sources (TikTok WoW%, Pinterest volume, Google Trends) → 5.0
    #   Editorial/qualitative sources (RSS, Reddit) → 4.0  (corroboration value)
    _EDITORIAL_SOURCES = {"editorial_rss", "reddit"}
    def _min_score(signal: dict) -> float:
        return 4.0 if signal.get("source") in _EDITORIAL_SOURCES else 5.0

    filtered = [(s, r) for s, r in scored_signals if r.score >= _min_score(s)]
    MIN_SCORE = "4.0–5.0"
    print(f"\n[4/5] Claude narrative generation (score ≥ {MIN_SCORE})...")
    print(f"  Generating for {len(filtered)} of {len(scored_signals)} signals "
          f"(editorial ≥4.0, others ≥5.0)...")

    results: list[tuple[dict, ScoreResult, dict]] = []
    narrative_errors = 0
    for i, (signal, score_result) in enumerate(filtered):
        title = signal.get("title") or signal.get("term") or f"signal-{i}"
        try:
            print(f"  Narrative ({i+1}/{len(filtered)}): {title[:55]}")
            narrative = generate_narrative(signal, score_result)
            results.append((signal, score_result, narrative))
        except Exception as e:
            print(f"  [WARN] Narrative failed for '{title}': {e}")
            narrative_errors += 1

    print(f"  Done: {len(results)} | Errors: {narrative_errors}")

    # 5. Write to DB
    print("\n[5/5] Writing to database...")
    db      = SessionLocal()
    created = 0
    updated = 0
    errors  = 0
    try:
        for signal, score_result, narrative in results:
            try:
                _, _, action = _write_trend_and_market(db, signal, score_result, narrative)
                if action.startswith("updated"):
                    updated += 1
                else:
                    created += 1
            except Exception as e:
                print(f"  [WARN] DB write failed: {e}")
                db.rollback()
                errors += 1
        db.commit()
        print(f"  Created: {created} | Updated: {updated} | Errors: {errors}")
    except Exception as e:
        db.rollback()
        print(f"  [ERROR] Commit failed: {e}")
    finally:
        db.close()

    print("\n" + "=" * 60)
    print(f"  {len(raw_signals)} scraped  →  {len(unique_signals)} unique  →  "
          f"{len(filtered)} passed threshold  →  {written} saved")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
