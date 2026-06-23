"""
Weekly Digest Agent
===================
Runs every Sunday. Compiles:
  - Top 5 signal movers (biggest score increases this week)
  - Top 5 new trends detected
  - Markets that resolved this week (correct vs incorrect calls)
  - Cross-platform confirmed trends
  - Score decay casualties (trends that dropped significantly)

Outputs:
  - Console summary (always)
  - HTML email digest (if SMTP configured)
  - JSON digest file for frontend display (always)

Usage:
    python -m agents.weekly_digest
    python -m agents.weekly_digest --send-email  # also sends email
"""
import sys
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent.parent
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from dotenv import load_dotenv
load_dotenv(_BACKEND / ".env", override=False)

from db.session import SessionLocal
from db.models import Trend, Market, MarketStatus, TrendScoreHistory

_DIGEST_FILE = _BACKEND / "data" / "weekly_digest.json"


def _score_change(trend: Trend, db, days: int = 7) -> float:
    """Score delta vs 7 days ago using history table."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    oldest = (
        db.query(TrendScoreHistory)
        .filter(TrendScoreHistory.trend_id == trend.id)
        .filter(TrendScoreHistory.recorded_at >= cutoff)
        .order_by(TrendScoreHistory.recorded_at.asc())
        .first()
    )
    if not oldest:
        return 0.0
    return round((trend.ai_score or 0) - oldest.score, 2)


def run(send_email: bool = False) -> dict:
    db = SessionLocal()
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)

    digest = {
        "generated_at": now.isoformat(),
        "week_of": week_ago.strftime("%b %d"),
        "new_trends": [],
        "top_movers": [],
        "resolved_markets": [],
        "cross_platform_confirmed": [],
        "score_casualties": [],
        "stats": {},
    }

    try:
        all_trends = db.query(Trend).all()
        total = len(all_trends)

        # ── New trends this week ──────────────────────────────────────────────
        new_trends = sorted(
            [t for t in all_trends if t.created_at and t.created_at >= week_ago],
            key=lambda t: t.ai_score or 0,
            reverse=True,
        )[:8]

        digest["new_trends"] = [
            {
                "id": t.id,
                "name": t.name,
                "score": t.ai_score,
                "source": t.source,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in new_trends
        ]

        # ── Top score movers ──────────────────────────────────────────────────
        movers = []
        for t in all_trends:
            delta = _score_change(t, db)
            if abs(delta) >= 0.3:
                movers.append((t, delta))
        movers.sort(key=lambda x: abs(x[1]), reverse=True)

        digest["top_movers"] = [
            {
                "id": t.id,
                "name": t.name,
                "score": t.ai_score,
                "delta": delta,
                "direction": "up" if delta > 0 else "down",
            }
            for t, delta in movers[:6]
        ]

        # ── Resolved markets this week ────────────────────────────────────────
        resolved = (
            db.query(Market)
            .filter(Market.resolved_at >= week_ago)
            .all()
        )

        digest["resolved_markets"] = [
            {
                "id": m.id,
                "question": m.question,
                "outcome": m.status.value if m.status else "unknown",
                "total_pool": m.total_volume,
                "trend_name": m.trend.name if m.trend else "",
            }
            for m in resolved
        ]

        # ── Cross-platform confirmed ──────────────────────────────────────────
        cross = [
            t for t in all_trends
            if (t.platform_count or 1) >= 2
        ]
        digest["cross_platform_confirmed"] = [
            {
                "id": t.id,
                "name": t.name,
                "score": t.ai_score,
                "platforms": t.confirmed_sources or t.source,
                "platform_count": t.platform_count or 1,
            }
            for t in sorted(cross, key=lambda t: t.ai_score or 0, reverse=True)[:5]
        ]

        # ── Score casualties (significant drops) ──────────────────────────────
        casualties = [(t, d) for t, d in movers if d <= -0.5]
        digest["score_casualties"] = [
            {
                "name": t.name,
                "score": t.ai_score,
                "delta": delta,
            }
            for t, delta in casualties[:4]
        ]

        # ── Stats ──────────────────────────────────────────────────────────────
        digest["stats"] = {
            "total_trends": total,
            "new_this_week": len(new_trends),
            "markets_resolved": len(resolved),
            "cross_platform_count": len(cross),
            "top_score": max((t.ai_score or 0) for t in all_trends) if all_trends else 0,
        }

        # ── Save JSON ─────────────────────────────────────────────────────────
        _DIGEST_FILE.parent.mkdir(exist_ok=True)
        _DIGEST_FILE.write_text(json.dumps(digest, indent=2))
        print(f"[digest] Saved to {_DIGEST_FILE}")

        # ── Console summary ───────────────────────────────────────────────────
        print(f"\n{'='*60}")
        print(f"  Fashion Futures — Weekly Digest ({digest['week_of']})")
        print(f"{'='*60}")
        print(f"  {len(new_trends)} new trends · {len(resolved)} markets resolved · {len(cross)} cross-platform confirmed")
        print(f"\n  Top new signals:")
        for t in digest["new_trends"][:5]:
            print(f"    {t['score']:.1f}  {t['name'][:45]}  [{t['source']}]")
        if digest["top_movers"]:
            print(f"\n  Biggest movers:")
            for m in digest["top_movers"][:4]:
                arrow = "↑" if m["delta"] > 0 else "↓"
                print(f"    {arrow} {abs(m['delta']):+.2f}  {m['name'][:40]}")

        # ── Email ──────────────────────────────────────────────────────────────
        if send_email:
            _send_digest_email(digest)

    finally:
        db.close()

    return digest


def _send_digest_email(digest: dict):
    from agents.alert_dispatcher import _send_email

    recipient = os.getenv("DIGEST_EMAIL")
    if not recipient:
        print("[digest] No DIGEST_EMAIL set — skipping email")
        return

    new_html = "".join(
        f'<tr><td style="padding:6px 12px;font-family:Georgia,serif;font-size:15px">{t["name"]}</td>'
        f'<td style="padding:6px 12px;color:#d4a853;text-align:right">{t["score"]:.1f}</td>'
        f'<td style="padding:6px 12px;color:rgba(245,240,235,0.4);font-size:11px">{t["source"]}</td></tr>'
        for t in digest["new_trends"]
    )

    body = f"""
<html><body style="font-family:sans-serif;background:#080808;color:#f5f0eb;padding:32px;max-width:600px">
  <h2 style="font-family:Georgia,serif;font-weight:300;color:#d4a853">
    Fashion Futures · Weekly Signal Digest
  </h2>
  <p style="color:rgba(245,240,235,0.5);font-size:12px">Week of {digest['week_of']}</p>

  <div style="display:flex;gap:24px;margin:24px 0">
    <div style="text-align:center">
      <p style="font-family:Georgia,serif;font-size:36px;color:#d4a853;margin:0">{digest['stats']['new_this_week']}</p>
      <p style="font-size:10px;letter-spacing:0.15em;text-transform:uppercase;color:rgba(245,240,235,0.4)">New Trends</p>
    </div>
    <div style="text-align:center">
      <p style="font-family:Georgia,serif;font-size:36px;color:#d4a853;margin:0">{digest['stats']['markets_resolved']}</p>
      <p style="font-size:10px;letter-spacing:0.15em;text-transform:uppercase;color:rgba(245,240,235,0.4)">Resolved</p>
    </div>
    <div style="text-align:center">
      <p style="font-family:Georgia,serif;font-size:36px;color:#d4a853;margin:0">{digest['stats']['cross_platform_count']}</p>
      <p style="font-size:10px;letter-spacing:0.15em;text-transform:uppercase;color:rgba(245,240,235,0.4)">Cross-Platform</p>
    </div>
  </div>

  <h3 style="font-family:Georgia,serif;font-weight:300;border-top:1px solid rgba(255,255,255,0.09);padding-top:20px">
    New This Week
  </h3>
  <table style="width:100%;border-collapse:collapse">{new_html}</table>

  <p style="margin-top:32px">
    <a href="http://localhost:3000"
       style="display:inline-block;padding:10px 20px;background:#d4a853;color:#080808;
              text-decoration:none;font-size:11px;letter-spacing:0.15em;text-transform:uppercase">
      Open Markets →
    </a>
  </p>
</body></html>
"""
    _send_email(recipient, f"Fashion Futures Digest — {digest['week_of']}", body)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--send-email", action="store_true")
    args = parser.parse_args()
    run(send_email=args.send_email)
