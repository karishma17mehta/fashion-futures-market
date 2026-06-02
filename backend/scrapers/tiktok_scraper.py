"""
TikTok Fashion Trend Scraper
============================
Uses TikTokApi (unofficial) to pull hashtag view counts and video counts
for fashion-relevant terms. Tracks week-over-week growth by comparing
current counts against a local cache (JSON file).

Data returned per hashtag:
    - view_count     : total hashtag views (cumulative)
    - video_count    : total videos posted with this hashtag
    - wow_pct        : week-over-week % change in views (requires prior cache)
    - velocity_tier  : 'explosive' / 'rising' / 'stable' / 'declining'

Scoring integration:
    Results feed into TrendSignalData as:
        tiktok_growth_pct = wow_pct   (used by cross_platform_score)

    When wow_pct is unavailable (first run, no cache), we fall back to
    a tier-based proxy derived from absolute view count milestones.

Usage:
    python -m scrapers.tiktok_scraper              # run and print
    python -m scrapers.tiktok_scraper --update-db  # run and write to DB
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── fashion hashtag seed list ────────────────────────────────────────────────
# Organised by category. Add new terms here — scraper handles the rest.

FASHION_HASHTAGS: list[str] = [
    # ── Aesthetics / macro trends ─────────────────────────────────────────────
    "quietluxury",
    "quietluxuryfashion",
    "olmoneyaesthetic",
    "olmoneyoutfit",
    "corporategirlie",
    "officewear",
    "officeootd",
    "balletcore",
    "coquetteaesthetic",
    "darkacademia",
    "cottagecoreoutfit",
    "y2kfashion",
    "dopaminedressing",
    "gorpcore",
    "maximalistfashion",
    "vintageaesthetic",
    "grungefashion",
    "gothfashion",
    "preppy",
    "streetwear",
    # ── Garments trending now ─────────────────────────────────────────────────
    "widelegtrousers",
    "barreljeansoutfit",
    "loafershoes",
    "maryjaneshoes",
    "trenchcoat",
    "leathertrousers",
    "sartorialtailoring",
    "sheeroutfit",
    "lacefashion",
    "crochetoutfit",
    "balloonpants",
    "cargotrousers",
    "plisseskirt",
    # ── Accessories ───────────────────────────────────────────────────────────
    "statementbelt",
    "brooch",
    "statementjewelry",
    "satchelbag",
    "buckethat",
    # ── Beauty / nails ────────────────────────────────────────────────────────
    "glassskinmakeup",
    "cherryredlips",
    "mismatchednails",
    "summernails2026",
    "nailart",
    "glittermakeup",
    "avantgardemakeup",
    "icybluenails",
    # ── Brands / collabs with search momentum ────────────────────────────────
    "coachbag",
    "coachoutfit",
    "moonswatch",
    "isabelmarant",
    "depopfinds",
    "thriftflip",
    "vintagefashion",
    "vintagefinds",
]

# ── Cache ─────────────────────────────────────────────────────────────────────
_CACHE_FILE = Path(__file__).parent / "_tiktok_cache.json"


def _load_cache() -> dict:
    if _CACHE_FILE.exists():
        try:
            return json.loads(_CACHE_FILE.read_text())
        except Exception:
            return {}
    return {}


def _save_cache(cache: dict) -> None:
    _CACHE_FILE.write_text(json.dumps(cache, indent=2))


# ── WoW calculation ───────────────────────────────────────────────────────────

_MIN_CACHE_AGE_DAYS = 6  # require at least 6 days between readings for valid WoW


def _calc_wow_pct(current_views: int, prior: dict | None) -> Optional[float]:
    """
    Calculate week-over-week % change in view count.
    Returns None if no prior data exists OR if prior reading is too recent
    (less than 6 days old) — a same-day re-run should not produce ~0% WoW.
    """
    if prior is None:
        return None
    prior_views = prior.get("view_count", 0)
    if prior_views <= 0:
        return None

    # Guard: don't compute WoW from readings taken the same day
    scraped_at = prior.get("scraped_at")
    if scraped_at:
        try:
            prior_dt = datetime.fromisoformat(scraped_at)
            age_days = (datetime.now(tz=timezone.utc) - prior_dt).total_seconds() / 86400
            if age_days < _MIN_CACHE_AGE_DAYS:
                return None  # too fresh — fall back to proxy
        except Exception:
            pass

    return round((current_views - prior_views) / prior_views * 100, 1)


def _velocity_tier(view_count: int, wow_pct: Optional[float]) -> str:
    """
    Categorise trend velocity for display / fallback scoring.
    Priority: use wow_pct if available; fall back to view count milestones.
    """
    if wow_pct is not None:
        if wow_pct >= 200:  return "explosive"
        if wow_pct >= 50:   return "rising"
        if wow_pct >= 5:    return "stable"
        return "declining"
    # First-run fallback — proxy from absolute view count
    if view_count >= 5_000_000_000:  return "explosive"   # 5B+
    if view_count >= 1_000_000_000:  return "rising"       # 1B+
    if view_count >= 100_000_000:    return "stable"        # 100M+
    return "emerging"


def _proxy_wow_pct(view_count: int, video_count: int) -> float:
    """
    When no prior cache exists, produce a rough proxy WoW % from
    the ratio of view_count to video_count (engagement density)
    and the absolute view count scale.

    This is intentionally conservative — used only for first run.
    Real WoW data from subsequent runs will replace this.
    """
    if video_count <= 0:
        return 10.0  # default neutral
    views_per_video = view_count / video_count
    # High views/video + massive scale → likely still growing fast
    if view_count >= 5_000_000_000 and views_per_video > 5000:
        return 150.0
    if view_count >= 1_000_000_000:
        return 80.0
    if view_count >= 100_000_000:
        return 40.0
    if view_count >= 10_000_000:
        return 20.0
    return 10.0


# ── Core scraper ──────────────────────────────────────────────────────────────

async def _scrape_hashtags(hashtags: list[str]) -> list[dict]:
    """
    Query TikTokApi for each hashtag and return enriched signal dicts.
    Handles individual failures gracefully — one bad hashtag won't kill the run.
    """
    from TikTokApi import TikTokApi  # local import — heavy library

    cache = _load_cache()
    now_ts = datetime.now(tz=timezone.utc).isoformat()
    results: list[dict] = []

    async with TikTokApi() as api:
        await api.create_sessions(headless=True, num_sessions=1, sleep_after=3)

        for hashtag in hashtags:
            try:
                tag = api.hashtag(name=hashtag)
                info = await tag.info()

                challenge = (
                    info.get("challengeInfo", {})
                        .get("statsV2")
                    or info.get("challengeInfo", {})
                        .get("stats", {})
                )
                view_count  = int(challenge.get("viewCount",  0))
                video_count = int(challenge.get("videoCount", 0))

                prior = cache.get(hashtag)
                wow_pct = _calc_wow_pct(view_count, prior)

                # Use proxy if first run
                effective_wow = wow_pct if wow_pct is not None else _proxy_wow_pct(view_count, video_count)

                result = {
                    "hashtag":      hashtag,
                    "view_count":   view_count,
                    "video_count":  video_count,
                    "wow_pct":      wow_pct,             # None on first run
                    "effective_wow": effective_wow,      # always a number
                    "velocity_tier": _velocity_tier(view_count, wow_pct),
                    "scraped_at":   now_ts,
                    "source":       "tiktok",
                    # Pipeline-compatible fields
                    "title":        f"#{hashtag}",
                    "description":  (
                        f"TikTok #{hashtag}: {view_count:,} views, "
                        f"{video_count:,} videos. "
                        f"WoW: {wow_pct:+.1f}%" if wow_pct is not None
                        else f"TikTok #{hashtag}: {view_count:,} views, {video_count:,} videos."
                    ),
                    "tiktok_growth_pct": effective_wow,
                }

                # Update cache with current reading
                cache[hashtag] = {
                    "view_count":  view_count,
                    "video_count": video_count,
                    "scraped_at":  now_ts,
                }

                results.append(result)
                tier = result["velocity_tier"]
                print(
                    f"[tiktok] #{hashtag:<30} "
                    f"views={view_count:>15,}  "
                    f"wow={f'{wow_pct:+.1f}%' if wow_pct is not None else 'first-run':>10}  "
                    f"[{tier}]"
                )
                await asyncio.sleep(1.5)  # polite delay

            except Exception as exc:
                print(f"[tiktok] SKIP #{hashtag}: {exc}")
                continue

    _save_cache(cache)
    return results


# ── Fashion filter ────────────────────────────────────────────────────────────

# Minimum view count to bother scoring — filters out dead / typo hashtags
_MIN_VIEWS = 100_000


def filter_fashion_signals(raw: list[dict]) -> list[dict]:
    """
    Keep only hashtags with sufficient volume to be meaningful signals.
    Sort by effective_wow descending so the hottest trends surface first.
    """
    filtered = [r for r in raw if r["view_count"] >= _MIN_VIEWS]
    filtered.sort(key=lambda x: x["effective_wow"], reverse=True)
    return filtered


# ── Public entry point ────────────────────────────────────────────────────────

def scrape(hashtags: Optional[list[str]] = None) -> list[dict]:
    """
    Synchronous wrapper. Returns a list of signal dicts ready for the pipeline.

    Each dict includes:
        source             : "tiktok"
        title              : "#hashtagname"
        description        : human-readable summary
        tiktok_growth_pct  : WoW % (or proxy on first run)
        velocity_tier      : "explosive" | "rising" | "stable" | "declining"
        view_count         : raw view count
        video_count        : raw video count
    """
    targets = hashtags or FASHION_HASHTAGS
    print(f"[tiktok_scraper] Querying {len(targets)} hashtags...")

    raw     = asyncio.run(_scrape_hashtags(targets))
    signals = filter_fashion_signals(raw)

    print(f"[tiktok_scraper] {len(raw)} queried → {len(signals)} above threshold")
    return signals


# ── Pipeline scoring bridge ───────────────────────────────────────────────────

def signals_to_trend_data(signals: list[dict]):
    """
    Convert TikTok signals to TrendSignalData objects for formula scoring.
    Import here to avoid circular imports when used standalone.
    """
    _backend = Path(__file__).resolve().parent.parent
    if str(_backend) not in sys.path:
        sys.path.insert(0, str(_backend))
    from scoring.formula import TrendSignalData

    trend_data = []
    for s in signals:
        data = TrendSignalData(
            trend_name       = s["title"],
            monthly_change_pct = s["effective_wow"],  # best proxy we have
            tiktok_growth_pct  = s["effective_wow"],
        )
        trend_data.append((s, data))
    return trend_data


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="TikTok fashion hashtag scraper")
    parser.add_argument("--update-db", action="store_true", help="Write results to DB")
    parser.add_argument("--hashtags", nargs="*", help="Override hashtag list")
    parser.add_argument("--min-wow", type=float, default=0.0, help="Minimum WoW% filter")
    args = parser.parse_args()

    signals = scrape(args.hashtags)

    if args.min_wow > 0:
        signals = [s for s in signals if s["effective_wow"] >= args.min_wow]

    print()
    print(f"{'HASHTAG':<35} {'VIEWS':>15} {'VIDEOS':>10} {'WoW%':>10} {'TIER':<12}")
    print("-" * 80)
    for s in signals:
        wow_str = f"{s['wow_pct']:+.1f}%" if s["wow_pct"] is not None else "first-run"
        print(
            f"#{s['hashtag']:<34} "
            f"{s['view_count']:>15,} "
            f"{s['video_count']:>10,} "
            f"{wow_str:>10} "
            f"{s['velocity_tier']:<12}"
        )

    if args.update_db:
        print("\nWriting to DB...")
        _backend = Path(__file__).resolve().parent.parent
        sys.path.insert(0, str(_backend))
        from dotenv import load_dotenv
        load_dotenv(_backend / ".env", override=True)

        from scoring.formula import compute_score
        from ai.trend_scorer import generate_narrative
        from db.session import SessionLocal
        from db.models import Trend, Market, TrendStatus, MarketStatus
        import uuid
        from datetime import timedelta

        trend_pairs = signals_to_trend_data(signals)
        db = SessionLocal()
        written = 0
        # TikTok proxy scores cluster around 4–5 on first run — lower threshold
        # so we get baseline entries. Real WoW data will update scores next week.
        MIN_SCORE = 4.0 if all(s["wow_pct"] is None for s in signals) else 5.0
        print(f"  Score threshold: {MIN_SCORE} ({'proxy/first-run mode' if MIN_SCORE == 4.0 else 'real WoW mode'})")
        try:
            for signal, trend_data in trend_pairs:
                score_result = compute_score(trend_data)
                if score_result.score < MIN_SCORE:
                    continue

                # Skip if already in DB
                existing = db.query(Trend).filter(Trend.name == signal["title"]).first()
                if existing:
                    # Update score if we now have real WoW data
                    if signal["wow_pct"] is not None:
                        existing.ai_score        = score_result.score
                        existing.signal_velocity = score_result.components.get("velocity", 0.0)
                        print(f"  Updated: {signal['title']} → {score_result.score}")
                    continue

                narrative = generate_narrative(signal, score_result)
                now = datetime.now(tz=timezone.utc)
                trend_id  = str(uuid.uuid4())
                market_id = str(uuid.uuid4())

                trend = Trend(
                    id              = trend_id,
                    name            = narrative.get("trend_name") or signal["title"],
                    description     = narrative.get("thesis", signal["description"]),
                    ai_score        = score_result.score,
                    ai_thesis       = narrative.get("thesis", ""),
                    source          = "tiktok",
                    signal_velocity = score_result.components.get("velocity", 0.0),
                    status          = TrendStatus.emerging,
                    created_at      = now.replace(tzinfo=None),
                )
                market = Market(
                    id                  = market_id,
                    trend_id            = trend_id,
                    question            = narrative.get("resolution_question", f"Will {trend.name} reach mainstream adoption within 90 days?"),
                    resolution_date     = (now + timedelta(days=90)).replace(tzinfo=None),
                    resolution_criteria = narrative.get("resolution_question", ""),
                    yes_price           = 0.5,
                    no_price            = 0.5,
                    liquidity_param     = 100.0,
                    total_volume        = 0,
                    status              = MarketStatus.open,
                    created_at          = now.replace(tzinfo=None),
                )
                db.add(trend)
                db.add(market)
                written += 1
                print(f"  Added: {trend.name} (score={score_result.score})")

            db.commit()
            print(f"\nDone. Written: {written}")
        except Exception as e:
            db.rollback()
            print(f"DB error: {e}")
        finally:
            db.close()
