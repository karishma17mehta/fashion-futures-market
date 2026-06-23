"""
Trend Report Generator
======================
Compiles the top scored trends into a structured, brand-facing trend report —
the kind of forward-looking forecast a merchandising or buying team would buy
from WGSN, Edited, or Heuritech.

The signal engine and deterministic scoring do the quantitative work. Claude
adds two things on top, in a single call:

  1. An executive read on the season — the macro story the signals are telling.
  2. A per-trend MERCH BRIEF — the commercial translation a buyer actually needs:
     category, where it sits in the assortment, price tier, peak timing, buy
     depth guidance, and markdown risk.

Output is written to data/trend_report.json and served by api/routes/reports.py.

Run manually:
    python -m agents.trend_report
    python -m agents.trend_report --limit 10 --min-score 6
"""
from __future__ import annotations

import argparse
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import anthropic
import httpx
from dotenv import load_dotenv

# Allow running both as a module and as a script
try:
    from db.session import SessionLocal
    from db.models import Trend, TrendStatus, Market
except ImportError:  # pragma: no cover - path shim for direct execution
    import sys
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from db.session import SessionLocal
    from db.models import Trend, TrendStatus, Market

load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"), override=False)

_OUT_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "trend_report.json"
_MODEL = "claude-sonnet-4-6"

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


REPORT_PROMPT = """You are the head of trend forecasting at a fashion intelligence firm, writing the commercial read for a buying and merchandising audience. A deterministic scoring engine has already ranked these emerging trends from real signal data across editorial, social, search, and resale platforms. You do not change any numbers. You translate the signals into buying decisions.

Reporting period: {period}
Trends (already scored, strongest first):
{trend_block}

Write a trend report. Respond in JSON with this exact structure:
{{
  "season_label": "A short evocative name for the macro story these trends tell, e.g. 'Quiet Excess' or 'Engineered Softness'. 2-4 words.",
  "executive_summary": "Two tight paragraphs for a buying director. First paragraph: the macro read — what cultural and commercial forces connect these signals this period. Second paragraph: the headline action — where to lean in, where to hold, what the risk is. Concrete, confident, no hedging filler. No em dashes.",
  "briefs": {{
    "<trend_id>": {{
      "headline": "One punchy sentence a buyer would underline.",
      "category": "Primary product category, e.g. 'Outerwear', 'Denim', 'Footwear', 'Knitwear', 'Accessories'.",
      "assortment_role": "Where it sits: 'Core', 'Fashion', 'Statement', or 'Test'.",
      "price_tier": "'Entry', 'Mid', 'Premium', or 'Luxury'.",
      "peak_window": "When it likely peaks for consumers, e.g. 'Spring 2027' or 'Holiday 2026'. Be specific to the timeline signal.",
      "buy_guidance": "One sentence of concrete depth/breadth guidance, e.g. 'Buy narrow and deep in core colours; chase if sell-through clears 60% in four weeks.'",
      "markdown_risk": "'Low', 'Medium', or 'High', plus a 4-8 word reason.",
      "confidence": "'High', 'Medium', or 'Speculative' — your conviction this becomes a real buy, grounded in the score and cross-platform confirmation."
    }}
  }}
}}

Every trend in the list must have a brief keyed by its exact id. Be specific and commercial. Do not invent scores. No em dashes anywhere."""


def _fetch_image_url(trend_name: str, category: str | None, access_key: str | None) -> str | None:
    """Fetch one landscape fashion photo from Unsplash.
    Uses the merch category (e.g. 'Knitwear') as the query — more reliable than
    specific trend names. Falls back to 'fashion editorial' if still no results.
    Returns None silently if no key or request fails.
    Free tier: 50 req/hour. Set UNSPLASH_ACCESS_KEY in .env to enable.
    """
    if not access_key:
        return None
    queries = []
    if category:
        queries.append(f"fashion {category}")
    # First word of trend name as lightweight backup
    first = trend_name.split()[0].lower()
    if first not in (category or "").lower():
        queries.append(f"fashion {first}")
    queries.append("fashion editorial style")

    for q in queries:
        try:
            resp = httpx.get(
                "https://api.unsplash.com/photos/random",
                params={"query": q, "orientation": "landscape", "client_id": access_key},
                timeout=6,
            )
            if resp.status_code == 200:
                return resp.json()["urls"]["regular"]
        except Exception:
            pass
    return None


def _gather_trends(db, limit: int, min_score: float):
    """Top non-dead trends, cross-confirmed surfaced first, then by score."""
    trends = (
        db.query(Trend)
        .filter(Trend.ai_score >= min_score)
        .filter(Trend.status != TrendStatus.dead)
        .order_by(
            (Trend.platform_count >= 2).desc(),
            Trend.ai_score.desc(),
        )
        .limit(limit)
        .all()
    )
    return trends


def _trend_payload(t: Trend, db) -> dict:
    """The structural facts about a trend — everything except the merch narrative."""
    market = (
        db.query(Market)
        .filter(Market.trend_id == t.id)
        .order_by(Market.total_volume.desc())
        .first()
    )
    sources = [s.strip() for s in (t.confirmed_sources or t.source or "").split(",") if s.strip()]
    return {
        "id": t.id,
        "name": t.name,
        "description": t.description or "",
        "score": round(t.ai_score or 0.0, 1),
        "velocity": round(t.signal_velocity or 0.0, 1),
        "status": t.status.value if t.status else "emerging",
        "platform_count": t.platform_count or 1,
        "sources": sources,
        "cross_confirmed": (t.platform_count or 1) >= 2,
        "thesis": t.ai_thesis or "",
        "market_question": market.question if market else None,
    }


def _claude_layer(payloads: list[dict], period: str) -> dict:
    """One Claude call → season label, exec summary, and a brief per trend."""
    trend_block = "\n\n".join(
        f"id: {p['id']}\n"
        f"name: {p['name']}\n"
        f"score: {p['score']}/10  velocity: {p['velocity']}%  "
        f"status: {p['status']}  cross_confirmed: {p['cross_confirmed']} "
        f"({p['platform_count']} platforms: {', '.join(p['sources']) or 'n/a'})\n"
        f"thesis: {p['thesis'][:600]}"
        for p in payloads
    )

    message = client.messages.create(
        model=_MODEL,
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": REPORT_PROMPT.format(period=period, trend_block=trend_block),
        }],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def generate_report(limit: int = 8, min_score: float = 5.0) -> dict:
    """Build the full report object and persist it to data/trend_report.json."""
    db = SessionLocal()
    try:
        trends = _gather_trends(db, limit, min_score)
        if not trends:
            raise RuntimeError("No trends meet the threshold — lower --min-score or seed data first.")

        payloads = [_trend_payload(t, db) for t in trends]
        period = datetime.now(timezone.utc).strftime("%B %Y")
        narrative = _claude_layer(payloads, period)

        unsplash_key = os.getenv("UNSPLASH_ACCESS_KEY")
        briefs = narrative.get("briefs", {})
        items = []
        for p in payloads:
            p["brief"] = briefs.get(p["id"], {})
            category = p["brief"].get("category")
            p["image_url"] = _fetch_image_url(p["name"], category, unsplash_key)
            items.append(p)

        report = {
            "id": str(uuid.uuid4())[:8],
            "title": "Forward Signals",
            "season_label": narrative.get("season_label", "Emerging Signals"),
            "period": period,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "prepared_by": os.getenv("REPORT_AUTHOR", "Karishma Mehta"),
            "executive_summary": narrative.get("executive_summary", ""),
            "methodology": (
                "Trends are surfaced by a continuous signal engine scanning editorial, "
                "social, search, and resale platforms, then scored 0 to 10 by a deterministic "
                "formula on velocity, acceleration, novelty, volume, and cross-platform "
                "confirmation. Numbers are reproducible from source data. The commercial read "
                "is the analyst layer on top of the signal."
            ),
            "trend_count": len(items),
            "trends": items,
        }

        _OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        _OUT_FILE.write_text(json.dumps(report, indent=2))
        return report
    finally:
        db.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Generate the fashion trend report.")
    ap.add_argument("--limit", type=int, default=8, help="How many trends to include.")
    ap.add_argument("--min-score", type=float, default=5.0, help="Minimum signal score.")
    args = ap.parse_args()

    rep = generate_report(limit=args.limit, min_score=args.min_score)
    print(f"Report '{rep['season_label']}' generated with {rep['trend_count']} trends.")
    print(f"Written to: {_OUT_FILE}")
