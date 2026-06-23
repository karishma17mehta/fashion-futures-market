"""
Pinterest Trends Scraper
========================
Pulls real trend data from Pinterest's internal API — no login required.

Two data sources used:
  1. /top_trends_filtered/  — Pinterest's own top trending terms, with
                              yoy/mom/wow changes + normalized volume.
                              Filtered to fashion-relevant terms via keyword matching.

  2. /metrics/              — Arbitrary keyword lookup returning 53-week time
                              series + growth rates for any term we supply.
                              Requires the request to originate from a live
                              trends.pinterest.com browser session (Playwright).

Data returned per trend:
    term               : keyword string
    yoy_change_pct     : year-over-year % (float, may be None)
    mom_change_pct     : month-over-month % (float)
    wow_change_pct     : week-over-week % (float)
    normalized_volume  : 0–100 Pinterest search mass
    weekly_volumes     : list of 13 most recent weekly normalizedCount values
    seasonality_score  : 0.0–1.0 (1.0 = purely seasonal)
    source             : "pinterest"

Value encoding for growth_rates from Pinterest API:
    Decimals represent fractional change, NOT percentages.
    e.g. mom_change = 0.95  →  +95% month-over-month
         mom_change = -0.3  →  -30% month-over-month
         mom_change = 10.0  →  +1000% month-over-month
    We multiply by 100 to get percentages for our scoring formula.

Usage:
    python -m scrapers.pinterest_scraper              # top trends
    python -m scrapers.pinterest_scraper --keywords "quiet luxury,brooch"
    python -m scrapers.pinterest_scraper --update-db
"""
from __future__ import annotations

import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── Fashion keyword filter ────────────────────────────────────────────────────
# Used to identify fashion-relevant terms in the top_trends endpoint
FASHION_KEYWORDS: set[str] = {
    # Garments
    "dress", "skirt", "trouser", "pant", "jeans", "denim", "jacket", "coat",
    "blazer", "suit", "top", "blouse", "shirt", "sweater", "knit", "cardigan",
    "hoodie", "bodysuit", "corset", "lingerie", "shorts", "mini", "midi", "maxi",
    "legging", "jumpsuit", "romper", "trench", "leather", "lace", "sheer",
    "crochet", "knitted", "velvet", "silk", "satin", "linen",
    # Footwear
    "shoe", "heel", "boot", "loafer", "sneaker", "sandal", "flat", "pump",
    "mule", "mary jane", "ballet flat", "platform",
    # Accessories
    "bag", "handbag", "purse", "tote", "clutch", "belt", "hat", "cap",
    "sunglasses", "jewelry", "necklace", "ring", "earring", "bracelet",
    "brooch", "pin", "scarf", "glove",
    # Beauty / nails
    "nail", "nails", "makeup", "lipstick", "blush", "liner", "lashes",
    "skincare", "glitter", "highlight", "contour",
    # Aesthetics / styles
    "aesthetic", "outfit", "ootd", "style", "fashion", "look", "wear",
    "core", "vibes", "inspo", "luxury", "vintage", "retro", "preppy",
    "grunge", "boho", "minimalist", "maximalist", "streetwear", "casual",
    "formal", "chic", "elegant", "edgy", "romantic",
    # Colours with fashion relevance
    "brown", "beige", "tan", "camel", "cream", "ivory", "sage", "forest",
    "burgundy", "wine", "mustard", "cobalt", "cerulean", "blush", "coral",
    # Brands that indicate fashion context
    "coach", "zara", "h&m", "mango", "reformation", "anthropologie",
    "free people", "revolve", "aritzia", "lululemon",
}


def _is_fashion_term(term: str) -> bool:
    """Return True if the term is likely fashion-related."""
    lower = term.lower()
    return any(kw in lower for kw in FASHION_KEYWORDS)


# ── Seed keyword list for /metrics/ lookups ───────────────────────────────────
FASHION_SEED_TERMS: list[str] = [
    # Core aesthetics
    "quiet luxury", "old money aesthetic", "corporate girlie", "office outfit",
    "ballet core", "coquette aesthetic", "dark academia outfit", "cottagecore",
    "gorpcore", "maximalist fashion", "vintage aesthetic", "goth fashion",
    "preppy style", "streetwear outfit", "dopamine dressing",
    # Trending garments
    "barrel jeans", "wide leg trousers", "leather trousers", "balloon pants",
    "cargo trousers", "sheer outfit", "lace dress", "crochet top",
    "trench coat outfit", "blazer outfit", "mini skirt outfit", "plisse skirt",
    # Footwear
    "loafer outfit", "mary jane shoes", "ballet flats", "kitten heels",
    "platform boots", "pointed toe heels",
    # Accessories
    "brooch outfit", "statement belt", "satchel bag", "statement jewelry",
    "layered necklace", "chunky belt",
    # Beauty / nails
    "nail art 2026", "summer nails 2026", "quiet luxury nails", "glazed donut nails",
    "lace nails", "mismatched nails", "avant garde makeup", "glass skin makeup",
    "cherry red lips", "icy blue nails",
    # Pinterest Predicts 2026 terms
    "80s fashion", "power dressing", "oversized suit", "chunky belt outfit",
    "poet aesthetic", "poetcore", "brooch aesthetic", "lapel shirt",
    "brown linen", "field jacket", "alien makeup", "opalescent makeup",
    "frosted makeup", "icy blue makeup",
    # Brand momentum
    "coach bag outfit", "isabel marant", "miu miu", "the row outfit",
    # Resale / intentional
    "capsule wardrobe", "thrift flip", "vintage finds outfit", "depop finds",
]

# Pinterest metrics accepts max 20 terms per request
_BATCH_SIZE = 20


# ── Core scraping ─────────────────────────────────────────────────────────────

async def _intercept_and_load(context) -> tuple[list[dict], list[dict]]:
    """
    Load the Pinterest Trends homepage, click through sections, and passively
    intercept all API responses. Returns (top_trend_items, metrics_items).

    Clicks "View shopping trends" to trigger the fashion/shopping metrics calls
    which give 13-week time series data for currently trending fashion terms.
    """
    page = await context.new_page()

    top_trend_items: list[dict] = []
    metrics_seen: set[str] = set()
    metrics_items: list[dict] = []

    async def on_response(resp):
        url = resp.url
        if resp.status != 200 or "trends.pinterest.com" not in url:
            return
        ct = resp.headers.get("content-type", "")
        if "json" not in ct:
            return
        try:
            body = await resp.json()
        except Exception:
            return

        if "top_trends_filtered" in url and isinstance(body, dict):
            items = body.get("values", [])
            top_trend_items.extend(items)

        elif "/metrics/" in url and isinstance(body, list) and body:
            for item in body:
                term = item.get("term", "")
                if term and term not in metrics_seen:
                    metrics_seen.add(term)
                    metrics_items.append(item)

    page.on("response", on_response)

    await page.goto("https://trends.pinterest.com", wait_until="networkidle", timeout=45000)
    await asyncio.sleep(4)

    # Click "View shopping trends" to trigger fashion-specific metrics calls
    try:
        btn = page.get_by_text("View shopping trends")
        await btn.click()
        await asyncio.sleep(4)
    except Exception:
        pass  # button may not always be present

    # Click "View search trends" to get another batch
    try:
        btn = page.get_by_text("View search trends")
        await btn.click()
        await asyncio.sleep(4)
    except Exception:
        pass

    await page.close()
    return top_trend_items, metrics_items


def _parse_top_trend(item: dict) -> dict:
    """
    Parse a top_trends_filtered item into our signal format.
    Growth values from this endpoint: raw value (e.g. 5 = +500%, -0.06 = -6%).
    """
    def _to_pct(change_dict):
        if not change_dict:
            return None
        val = change_dict.get("value")
        if val is None:
            return None
        return round(float(val) * 100, 1)

    return {
        "term":               item.get("term", ""),
        "yoy_change_pct":     _to_pct(item.get("yoy_change")),
        "mom_change_pct":     _to_pct(item.get("mom_change")),
        "wow_change_pct":     _to_pct(item.get("wow_change")),
        "normalized_volume":  float(item.get("normalizedCount") or item.get("searchCount") or 0),
        "seasonality_score":  float(item.get("seasonality_score", 0)),
        "weekly_volumes":     [],   # not in this endpoint
        "source":             "pinterest",
        "data_source":        "top_trends",
    }


def _parse_metrics_item(item: dict) -> dict:
    """
    Parse a /metrics/ item into our signal format.
    growth_rates values are fractional (0.95 = +95%, -0.3 = -30%).
    counts is a list of weekly {date, normalizedCount} objects.
    """
    gr = item.get("growth_rates") or {}

    def _gr_to_pct(val):
        if val is None:
            return None
        return round(float(val) * 100, 1)

    counts = item.get("counts", [])
    # Take last 13 weeks of normalizedCount values
    weekly = [c["normalizedCount"] for c in counts[-13:] if c.get("normalizedCount") is not None]
    normalized_volume = weekly[-1] if weekly else 0.0

    return {
        "term":               item.get("term", ""),
        "yoy_change_pct":     _gr_to_pct(gr.get("yoy_change")),
        "mom_change_pct":     _gr_to_pct(gr.get("mom_change")),
        "wow_change_pct":     _gr_to_pct(gr.get("wow_change")),
        "normalized_volume":  float(normalized_volume),
        "seasonality_score":  0.0,   # not in this endpoint
        "weekly_volumes":     weekly,
        "source":             "pinterest",
        "data_source":        "metrics",
    }


async def _run_scrape(seed_terms: Optional[list[str]] = None) -> list[dict]:
    """
    Main async scraping function.
    Passively intercepts Pinterest's own API calls as the page renders —
    more reliable than making additional requests after load.
    """
    from playwright.async_api import async_playwright

    all_results: dict[str, dict] = {}   # term → parsed signal

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
        )

        print("[pinterest] Loading trends.pinterest.com (intercepting API responses)...")
        top_items, metrics_items = await _intercept_and_load(context)
        print(f"[pinterest] Intercepted: {len(top_items)} top-trend items, {len(metrics_items)} metrics items")

        # ── Parse top_trends items (fashion-filtered) ─────────────────────────
        fashion_count = 0
        for item in top_items:
            term = item.get("term", "")
            if _is_fashion_term(term):
                parsed = _parse_top_trend(item)
                all_results[term] = parsed
                fashion_count += 1
        print(f"[pinterest] {fashion_count} fashion-relevant top trends")

        # ── Parse metrics items (full weekly series, higher quality) ──────────
        metrics_fashion = 0
        for item in metrics_items:
            term = item.get("term", "")
            if not term or not _is_fashion_term(term):
                continue
            parsed = _parse_metrics_item(item)
            existing = all_results.get(term)
            if existing and existing.get("data_source") == "top_trends":
                parsed["seasonality_score"] = existing["seasonality_score"]
            all_results[term] = parsed
            metrics_fashion += 1

            mom = parsed["mom_change_pct"]
            yoy = parsed["yoy_change_pct"]
            print(
                f"[pinterest] metrics  {term:<35} "
                f"mom={f'{mom:+.0f}%' if mom is not None else 'n/a':>8}  "
                f"yoy={f'{yoy:+.0f}%' if yoy is not None else 'n/a':>8}  "
                f"vol={parsed.get('normalized_volume', 0):>5.0f}  weeks={len(parsed.get('weekly_volumes', []))}"
            )
        if metrics_fashion:
            print(f"[pinterest] {metrics_fashion} fashion metrics items with weekly series")

        await browser.close()

    return list(all_results.values())


# ── Signal → scoring ──────────────────────────────────────────────────────────

def _to_score_data(signal: dict):
    """Convert a parsed Pinterest signal to TrendSignalData."""
    _backend = Path(__file__).resolve().parent.parent
    if str(_backend) not in sys.path:
        sys.path.insert(0, str(_backend))
    from scoring.formula import TrendSignalData

    return TrendSignalData(
        trend_name         = signal["term"],
        monthly_change_pct = signal.get("mom_change_pct"),
        weekly_change_pct  = signal.get("wow_change_pct"),
        yoy_change_pct     = signal.get("yoy_change_pct"),
        normalized_volume  = signal.get("normalized_volume"),
        weekly_volumes     = signal.get("weekly_volumes", []),
        on_pinterest       = signal.get("normalized_volume") or True,
    )


# ── Public entry point ────────────────────────────────────────────────────────

def scrape(seed_terms: Optional[list[str]] = None) -> list[dict]:
    """
    Synchronous entry point. Returns list of signal dicts ready for pipeline.
    """
    return asyncio.run(_run_scrape(seed_terms))


# ── CLI ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    _backend = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(_backend))
    from dotenv import load_dotenv
    load_dotenv(_backend / ".env", override=False)

    parser = argparse.ArgumentParser(description="Pinterest Trends scraper")
    parser.add_argument("--keywords", type=str, help="Comma-separated keywords to look up")
    parser.add_argument("--update-db", action="store_true", help="Write results to DB")
    parser.add_argument("--min-score", type=float, default=5.0, help="Minimum score to write")
    args = parser.parse_args()

    seed_terms = [k.strip() for k in args.keywords.split(",")] if args.keywords else None
    signals = scrape(seed_terms)

    # Sort by mom_change_pct descending
    signals.sort(key=lambda x: x.get("mom_change_pct") or 0, reverse=True)

    print()
    print(f"{'TERM':<38} {'MoM%':>8} {'YoY%':>8} {'VOL':>5} {'WKS':>4} {'SRC'}")
    print("-" * 80)
    for s in signals:
        mom = s.get("mom_change_pct")
        yoy = s.get("yoy_change_pct")
        print(
            f"{s['term']:<38} "
            f"{f'{mom:+.0f}%' if mom is not None else 'n/a':>8} "
            f"{f'{yoy:+.0f}%' if yoy is not None else 'n/a':>8} "
            f"{s.get('normalized_volume', 0):>5.0f} "
            f"{len(s.get('weekly_volumes', [])):>4} "
            f"{s.get('data_source', '?')}"
        )

    if args.update_db:
        from scoring.formula import compute_score
        from ai.trend_scorer import generate_narrative
        from db.session import SessionLocal
        from db.models import Trend, Market, TrendStatus, MarketStatus
        import uuid
        from datetime import timedelta

        print(f"\nScoring and writing to DB (threshold={args.min_score})...")
        db = SessionLocal()
        written = updated = skipped = 0
        try:
            for signal in signals:
                score_data = _to_score_data(signal)
                result = compute_score(score_data)

                # Always update if trend already exists and we have better data
                existing = db.query(Trend).filter(Trend.name == signal["term"]).first()
                if existing:
                    if result.score > existing.ai_score or len(signal.get("weekly_volumes", [])) >= 8:
                        existing.ai_score        = result.score
                        existing.signal_velocity = result.components.get("velocity", 0.0)
                        updated += 1
                        print(f"  Updated: {signal['term'][:40]} → {result.score}")
                    else:
                        skipped += 1
                    continue

                if result.score < args.min_score:
                    skipped += 1
                    continue

                narrative = generate_narrative(signal, result)
                now = datetime.now(tz=timezone.utc)
                tid  = str(uuid.uuid4())
                mid  = str(uuid.uuid4())

                trend = Trend(
                    id              = tid,
                    name            = narrative.get("trend_name") or signal["term"],
                    description     = narrative.get("thesis", ""),
                    ai_score        = result.score,
                    ai_thesis       = narrative.get("thesis", ""),
                    source          = "pinterest",
                    signal_velocity = result.components.get("velocity", 0.0),
                    status          = TrendStatus.emerging,
                    created_at      = now.replace(tzinfo=None),
                )
                market = Market(
                    id                  = mid,
                    trend_id            = tid,
                    question            = narrative.get("resolution_question", f"Will '{trend.name}' reach mainstream adoption?"),
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
                print(f"  Added: {trend.name[:45]} (score={result.score}, completeness={result.data_completeness:.0%})")

            db.commit()
            print(f"\nDone. Added: {written} | Updated: {updated} | Skipped: {skipped}")
        except Exception as e:
            db.rollback()
            print(f"DB error: {e}")
            raise
        finally:
            db.close()
