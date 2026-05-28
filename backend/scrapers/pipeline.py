"""
Fashion Futures Market — Scraper Pipeline
==========================================
Orchestrates all scrapers, deduplicates signals, scores via Claude AI,
and writes Trend + Market rows to PostgreSQL.

Usage:
    python -m scrapers.pipeline
    # or from backend/ directory:
    python scrapers/pipeline.py
"""
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Allow running as a script from the backend/ directory
_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from dotenv import load_dotenv
load_dotenv(_BACKEND_DIR / ".env", override=True)

from scrapers import whowhatwear_scraper, trendhunter_scraper, google_trends_scraper
from ai.trend_scorer import score_trend
from db.models import Trend, Market, TrendStatus, MarketStatus
from db.session import SessionLocal


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def _normalise(text: str) -> str:
    """Lower-case, strip, collapse whitespace."""
    return " ".join(text.lower().split())


def _jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def _token_set(text: str) -> set[str]:
    stop = {"a", "an", "the", "is", "in", "on", "at", "for", "to", "of", "and", "or", "with"}
    return {w for w in _normalise(text).split() if w not in stop and len(w) > 2}


def deduplicate(signals: list[dict], threshold: float = 0.45) -> list[dict]:
    """
    Remove near-duplicate signals using Jaccard similarity on title tokens.
    Keeps the first occurrence of each cluster.
    """
    unique: list[dict] = []
    for sig in signals:
        title = sig.get("title") or sig.get("term") or ""
        tokens = _token_set(title)
        is_dup = False
        for kept in unique:
            kept_title = kept.get("title") or kept.get("term") or ""
            if _jaccard(tokens, _token_set(kept_title)) >= threshold:
                is_dup = True
                break
        if not is_dup:
            unique.append(sig)
    return unique


# ---------------------------------------------------------------------------
# Signal normalisation
# ---------------------------------------------------------------------------

def _normalise_signal(raw: dict) -> dict:
    """Produce a uniform dict suitable for score_trend()."""
    signal: dict = {"source": raw.get("source", "unknown")}

    if "term" in raw:
        # Google Trends result
        signal["title"] = raw["term"]
        signal["description"] = (
            "Rising Google search term. Velocity (% change over 90 days): "
            f"{raw.get('velocity_score', 0.0)}. "
            f"Rising related queries: {', '.join(raw.get('rising_queries', []))}"
        )
        signal["velocity_score"] = raw.get("velocity_score", 0.0)
        signal["keywords"] = raw.get("rising_queries", [])
    else:
        signal["title"] = raw.get("title", "")
        signal["description"] = raw.get("description", "")
        signal["url"] = raw.get("url", "")
        signal["keywords"] = raw.get("keywords", [])
        signal["velocity_score"] = 0.0

    return signal


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def _write_trend_and_market(db, scored: dict, signal: dict) -> tuple[Trend, Market]:
    trend_id = str(uuid.uuid4())
    market_id = str(uuid.uuid4())
    now = datetime.now(tz=timezone.utc)
    resolution_date = now + timedelta(days=90)

    trend = Trend(
        id=trend_id,
        name=scored.get("trend_name") or signal.get("title", "Unknown Trend"),
        description=scored.get("thesis", ""),
        ai_score=float(scored.get("score", 0)),
        ai_thesis=scored.get("thesis", ""),
        source=signal.get("source", "unknown"),
        signal_velocity=float(signal.get("velocity_score", 0.0)),
        status=TrendStatus.emerging,
        created_at=now.replace(tzinfo=None),
    )

    question = (
        scored.get("resolution_question")
        or f"Will '{trend.name}' reach mainstream adoption within 90 days?"
    )
    resolution_criteria = (
        f"Resolved YES if {trend.name} appears in at least 3 major fashion publications "
        f"or reaches >70 Google Trends score by {resolution_date.strftime('%Y-%m-%d')}."
    )

    market = Market(
        id=market_id,
        trend_id=trend_id,
        question=question,
        resolution_date=resolution_date.replace(tzinfo=None),
        resolution_criteria=resolution_criteria,
        yes_price=0.5,
        no_price=0.5,
        liquidity_param=100.0,
        total_volume=0,
        status=MarketStatus.open,
        created_at=now.replace(tzinfo=None),
    )

    db.add(trend)
    db.add(market)
    return trend, market


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_pipeline() -> None:
    print("=" * 60)
    print("Fashion Futures Market — Scraper Pipeline")
    print("=" * 60)

    # 1. Run all scrapers
    print("\n[1/4] Running scrapers...")
    raw_signals: list[dict] = []

    print("  → WhoWhatWear...")
    raw_signals.extend(whowhatwear_scraper.scrape())

    print("  → TrendHunter...")
    raw_signals.extend(trendhunter_scraper.scrape())

    print("  → Google Trends...")
    raw_signals.extend(google_trends_scraper.scrape())

    total_found = len(raw_signals)
    print(f"  Total raw signals: {total_found}")

    # 2. Normalise + deduplicate
    print("\n[2/4] Deduplicating signals...")
    normalised = [_normalise_signal(s) for s in raw_signals]
    unique_signals = deduplicate(normalised)
    print(f"  Unique signals after dedup: {len(unique_signals)}")

    # 3. Score each signal via Claude
    print("\n[3/4] Scoring signals with Claude AI...")
    scored_pairs: list[tuple[dict, dict]] = []  # (signal, scored)
    score_errors = 0

    for i, signal in enumerate(unique_signals):
        title = signal.get("title") or signal.get("term") or f"signal-{i}"
        try:
            print(f"  Scoring ({i + 1}/{len(unique_signals)}): {title[:60]}")
            scored = score_trend(signal)
            scored_pairs.append((signal, scored))
        except Exception as exc:  # noqa: BLE001
            print(f"  [WARN] Scoring failed for '{title}': {exc}")
            score_errors += 1

    total_scored = len(scored_pairs)
    print(f"  Scored: {total_scored} | Errors: {score_errors}")

    # 4. Write to DB
    print("\n[4/4] Writing to database...")
    db = SessionLocal()
    written = 0
    write_errors = 0

    try:
        for signal, scored in scored_pairs:
            try:
                _write_trend_and_market(db, scored, signal)
                written += 1
            except Exception as exc:  # noqa: BLE001
                trend_name = scored.get("trend_name", signal.get("title", "?"))
                print(f"  [WARN] DB write failed for '{trend_name}': {exc}")
                db.rollback()
                write_errors += 1

        db.commit()
        print(f"  Written: {written} | Errors: {write_errors}")
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        print(f"  [ERROR] Commit failed: {exc}")
    finally:
        db.close()

    # Summary
    print("\n" + "=" * 60)
    print(
        f"{total_found} trends found, {total_scored} scored, {written} written to DB"
    )
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
