"""
Bulk-simplify the long tail of market questions with Claude.

Rewrites every market EXCEPT the 50 hand-crafted ones (in rewrite_markets.py)
into a sharp, one-sentence, gut-feel, verifiable question + a short criteria.

Usage:
    # against local DB
    python -m scripts.bulk_simplify_markets               # dry run (prints, no writes)
    python -m scripts.bulk_simplify_markets --execute

    # against cloud DB
    DATABASE_URL="postgresql://..." python -m scripts.bulk_simplify_markets --execute
"""
import sys
import os
import json
import argparse
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent.parent
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from dotenv import load_dotenv
load_dotenv(_BACKEND / ".env", override=True)

import anthropic
from db.session import SessionLocal
from db.models import Market, Trend
from scripts.rewrite_markets import REWRITES  # the 50 already-done IDs

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-6"
BATCH_SIZE = 12

PROMPT = """You are writing questions for a fashion prediction market where regular fashion-aware people bet YES/NO on whether a trend will go mainstream.

Rewrite each market question below so it is:
- ONE short sentence (max ~16 words), ending in a question mark
- Gut-feel and relatable — something a fashion-aware person has an instant opinion on
- Verifiable — resolvable by Googling or checking a named source by a clear date (use 2026 or 2027)
- Free of jargon like "diffusion", "macro trend", "trajectory", multi-clause legalese
- Still clearly about the SAME trend (keep the trend recognizable)

Also write a "criteria": ONE sentence stating concretely how it resolves YES (a named publication, platform search rank, retailer, or sales/resale signal + a date).

Here are the markets (JSON):
{batch}

Return ONLY a JSON array, one object per market, in the same order:
[{{"id": "<id>", "question": "<sharp question>", "criteria": "<one-sentence resolution>"}}]
No prose, no markdown fences."""


def _parse_json(raw: str):
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def _rewrite_batch(batch: list[dict]) -> list[dict]:
    msg = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": PROMPT.format(batch=json.dumps(batch, indent=2))}],
    )
    return _parse_json(msg.content[0].text)


def run(execute: bool = False, limit: int | None = None):
    db = SessionLocal()
    done_ids = set(REWRITES.keys())
    updated = 0
    failed = 0

    try:
        rows = (
            db.query(Market, Trend)
            .join(Trend, Market.trend_id == Trend.id)
            .all()
        )
        targets = [(m, t) for (m, t) in rows if m.id not in done_ids]
        if limit:
            targets = targets[:limit]

        print(f"[bulk_simplify] {len(targets)} markets to rewrite "
              f"({len(done_ids)} hand-crafted ones skipped)")
        print(f"[bulk_simplify] {'EXECUTE' if execute else 'DRY RUN'} — "
              f"{ (len(targets)+BATCH_SIZE-1)//BATCH_SIZE } batches of {BATCH_SIZE}\n")

        by_id = {m.id: m for (m, t) in targets}

        for i in range(0, len(targets), BATCH_SIZE):
            chunk = targets[i:i + BATCH_SIZE]
            payload = [{
                "id": m.id,
                "trend": t.name,
                "source": t.source,
                "current_question": m.question,
            } for (m, t) in chunk]

            bn = i // BATCH_SIZE + 1
            try:
                results = _rewrite_batch(payload)
            except Exception as e:
                print(f"  [batch {bn}] ERROR: {e}")
                failed += len(chunk)
                continue

            for r in results:
                mid = r.get("id")
                q = (r.get("question") or "").strip()
                c = (r.get("criteria") or "").strip()
                if not mid or mid not in by_id or not q:
                    continue
                print(f"  • {q}")
                if execute:
                    mk = by_id[mid]
                    mk.question = q
                    if c:
                        mk.resolution_criteria = c
                    updated += 1

            if execute:
                db.commit()
            print(f"  [batch {bn}] done ({min(i+BATCH_SIZE, len(targets))}/{len(targets)})\n")

        if execute:
            print(f"\n✓ Updated {updated} markets. Failed: {failed}")
        else:
            print(f"\nDRY RUN complete — would update ~{len(targets)} markets. Pass --execute.")

    except Exception as e:
        db.rollback()
        print(f"FATAL: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--limit", type=int, default=None, help="Only process first N (for testing)")
    args = parser.parse_args()
    run(execute=args.execute, limit=args.limit)
