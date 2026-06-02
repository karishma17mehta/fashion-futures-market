"""
Score Decay Agent
=================
Re-evaluates trend scores weekly. Trends that peaked and are no longer
generating fresh signals should see their scores decrease over time.

Decay rules:
  - Trends with no score update in > 14 days decay by 8% per week
  - Trends with status=mainstream or status=dead are excluded (already resolved)
  - Trends with fresh TikTok/Pinterest data (WoW cached < 7 days) get re-scored
  - Snapshots every score change into TrendScoreHistory for sparkline display

Also handles cross-platform confirmation bonuses:
  - Find trends with the same name from different sources
  - Merge them into a single "confirmed" trend with boosted score

Usage:
    python -m agents.score_decay             # dry run
    python -m agents.score_decay --execute   # write to DB
"""
import sys
import uuid
import argparse
from datetime import datetime, timedelta
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent.parent
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from dotenv import load_dotenv
load_dotenv(_BACKEND / ".env", override=True)

from db.session import SessionLocal
from db.models import Trend, TrendStatus, TrendScoreHistory


# ── Decay formula ─────────────────────────────────────────────────────────────

_DECAY_RATE     = 0.08   # 8% per week after 14 days stale
_MIN_SCORE      = 2.0    # floor — dead trends keep a minimum score
_STALE_DAYS     = 14     # no update after this → decay kicks in

def _apply_decay(score: float, weeks_stale: float) -> float:
    """Compound 8% weekly decay after the stale threshold."""
    decayed = score * ((1 - _DECAY_RATE) ** weeks_stale)
    return max(_MIN_SCORE, round(decayed, 2))


# ── Cross-platform deduplication / boost ──────────────────────────────────────

def _normalise_name(name: str) -> str:
    import re
    # Remove hashtag prefix, lowercase, strip punctuation
    name = re.sub(r"^#", "", name.lower().strip())
    name = re.sub(r"[^\w\s]", "", name)
    return " ".join(name.split())


def _names_match(a: str, b: str) -> bool:
    """
    True if two trend names refer to the same underlying trend.
    Claude renames signals (e.g. #balletcore → "Balletcore Aesthetic Fashion")
    so we use keyword overlap rather than exact string matching.
    """
    na, nb = _normalise_name(a), _normalise_name(b)
    if na == nb:
        return True
    # Space-stripped exact match (ballet core ↔ balletcore)
    if na.replace(" ", "") == nb.replace(" ", ""):
        return True

    # Significant keyword overlap — share ≥2 meaningful words
    stop = {"aesthetic", "revival", "fashion", "style", "trend", "core",
            "the", "of", "and", "is", "a", "an"}
    wa = {w for w in na.split() if w not in stop and len(w) > 3}
    wb = {w for w in nb.split() if w not in stop and len(w) > 3}
    if not wa or not wb:
        return False
    shared = wa & wb
    # Match if ≥2 words overlap, or if shared covers >60% of the smaller set
    smaller = min(len(wa), len(wb))
    return len(shared) >= 2 or (smaller > 0 and len(shared) / smaller >= 0.6)


def find_cross_platform_groups(db) -> list[list[Trend]]:
    """
    Return groups of trends that refer to the same trend from different sources.
    Each group has len >= 2.
    """
    trends = db.query(Trend).filter(
        Trend.status.in_([TrendStatus.emerging, TrendStatus.active])
    ).all()

    groups: list[list[Trend]] = []
    used: set[str] = set()

    for i, t1 in enumerate(trends):
        if t1.id in used:
            continue
        group = [t1]
        for t2 in trends[i+1:]:
            if t2.id in used:
                continue
            if t1.source != t2.source and _names_match(t1.name, t2.name):
                group.append(t2)
        if len(group) >= 2:
            for t in group:
                used.add(t.id)
            groups.append(group)

    return groups


def apply_cross_platform_boost(group: list[Trend], execute: bool, db) -> float:
    """
    Given a group of duplicate trends from different sources:
    1. Keep the highest-scoring one as the "primary"
    2. Boost its score by 0.5 per additional source (max +2.0)
    3. Mark confirmed_sources, platform_count
    4. Mark duplicates as dead (they'll be filtered from UI)
    Returns the new score.
    """
    primary = max(group, key=lambda t: t.ai_score or 0)
    others  = [t for t in group if t.id != primary.id]

    boost = min(2.0, 0.5 * len(others))
    new_score = min(10.0, round((primary.ai_score or 0) + boost, 2))
    sources = list({t.source for t in group})

    print(f"  Cross-platform: '{primary.name}' from {sources}")
    print(f"    Score: {primary.ai_score:.1f} → {new_score:.1f} (+{boost})")

    if execute:
        primary.ai_score       = new_score
        primary.platform_count = len(group)
        primary.confirmed_sources = ",".join(sources)
        primary.score_updated_at = datetime.utcnow()
        # Mark duplicates as dead so they don't appear in lists
        for t in others:
            t.status = TrendStatus.dead
            t.ai_thesis = f"[Merged into '{primary.name}' — duplicate cross-platform signal]"

    return new_score


# ── Score history snapshot ─────────────────────────────────────────────────────

def _snapshot(db, trend: Trend, score: float):
    snap = TrendScoreHistory(
        id          = str(uuid.uuid4()),
        trend_id    = trend.id,
        score       = score,
        velocity    = trend.signal_velocity or 0.0,
        recorded_at = datetime.utcnow(),
    )
    db.add(snap)


# ── Main ──────────────────────────────────────────────────────────────────────

def run(execute: bool = False) -> dict:
    db = SessionLocal()
    now = datetime.utcnow()
    stats = {
        "decayed":        0,
        "boosted":        0,
        "cross_platform": 0,
        "unchanged":      0,
        "snapshots":      0,
    }

    try:
        # ── 1. Score decay ────────────────────────────────────────────────────
        print("\n[score_decay] Step 1: Applying decay to stale trends...")
        stale_cutoff = now - timedelta(days=_STALE_DAYS)

        active_trends = db.query(Trend).filter(
            Trend.status.in_([TrendStatus.emerging, TrendStatus.active]),
        ).all()

        for trend in active_trends:
            last_update = trend.score_updated_at or trend.created_at or now
            age_days = (now - last_update).total_seconds() / 86400
            if age_days < _STALE_DAYS:
                stats["unchanged"] += 1
                continue

            weeks_stale = (age_days - _STALE_DAYS) / 7
            old_score = trend.ai_score or 5.0
            new_score = _apply_decay(old_score, weeks_stale)

            delta = new_score - old_score
            print(f"  '{trend.name[:40]}'  {old_score:.1f} → {new_score:.1f}  ({delta:+.2f}, {age_days:.0f}d stale)")

            if execute:
                trend.ai_score = new_score
                trend.score_updated_at = now
                _snapshot(db, trend, new_score)
                stats["snapshots"] += 1

                # If score dropped below 2.5, mark as dead
                if new_score <= 2.5:
                    trend.status = TrendStatus.dead
                    print(f"    → Marked dead (score too low)")

            stats["decayed"] += 1

        # ── 2. Cross-platform confirmation boost ──────────────────────────────
        print(f"\n[score_decay] Step 2: Cross-platform confirmation boost...")
        groups = find_cross_platform_groups(db)
        print(f"  Found {len(groups)} cross-platform groups")

        for group in groups:
            new_score = apply_cross_platform_boost(group, execute, db)
            stats["cross_platform"] += 1
            stats["boosted"] += len(group) - 1

            if execute:
                primary = max(group, key=lambda t: t.ai_score or 0)
                _snapshot(db, primary, new_score)
                stats["snapshots"] += 1

        if execute:
            db.commit()
            print(f"\n  Committed {stats['snapshots']} snapshots to history")

    except Exception as e:
        db.rollback()
        print(f"[score_decay] ERROR: {e}")
        raise
    finally:
        db.close()

    print(f"\n[score_decay] Done: {stats}")
    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    mode = "EXECUTE" if args.execute else "DRY RUN"
    print(f"Score Decay Agent [{mode}]")
    print("=" * 50)
    run(execute=args.execute)
