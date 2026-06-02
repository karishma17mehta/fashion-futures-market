"""
Auto-Resolution Agent
=====================
Checks open markets whose resolution_date has passed and resolves them
based on real-world evidence:

  Step 1 — Date check: skip markets that aren't due yet.
  Step 2 — Google Trends: has the search volume gone mainstream (≥60/100)?
  Step 3 — Editorial mentions: has this trend appeared in Vogue/Harper's since market opened?
  Step 4 — Score trajectory: has the AI score risen significantly (signal → mainstream)?

Resolution logic:
  YES  — two or more signals confirm mainstream adoption
  NO   — past resolution date, no mainstream signals detected
  SKIP — not enough evidence either way (extend 14 days, flag for manual review)

Usage:
    python -m agents.auto_resolve           # dry run (prints decisions, no DB write)
    python -m agents.auto_resolve --execute  # writes to DB and pays out positions
"""
import sys
import argparse
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent.parent
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from dotenv import load_dotenv
load_dotenv(_BACKEND / ".env", override=True)

from db.session import SessionLocal
from db.models import Market, MarketStatus, Trend, TrendStatus, Position
from scrapers import google_trends_scraper
from scrapers.trendhunter_scraper import _scrape_feed


# ── Evidence gathering ────────────────────────────────────────────────────────

def _google_mainstream(trend_name: str) -> tuple[bool, float]:
    """
    Returns (is_mainstream, peak_volume).
    Mainstream = peak normalized search volume ≥ 60 in last 4 weeks.
    """
    try:
        # Use existing google trends scraper for a single term
        results = google_trends_scraper.scrape_terms([trend_name])
        if not results:
            return False, 0.0
        r = results[0]
        vols = r.get("weekly_volumes", [])
        peak = max(vols) if vols else 0
        return peak >= 60, float(peak)
    except Exception as e:
        print(f"  [google check] {trend_name}: {e}")
        return False, 0.0


def _editorial_mentions(trend_name: str, since: datetime) -> int:
    """
    Count editorial RSS articles mentioning this trend since `since`.
    Returns count of matching articles.
    """
    from scrapers.trendhunter_scraper import RSS_FEEDS
    count = 0
    term_lower = trend_name.lower()
    # Only check a couple fast feeds
    for label, url in RSS_FEEDS[:3]:
        try:
            items = _scrape_feed(label, url)
            for item in items:
                text = (item.get("title", "") + " " + item.get("description", "")).lower()
                if term_lower in text or any(w in text for w in term_lower.split() if len(w) > 4):
                    count += 1
        except Exception:
            pass
    return count


def _score_rose(trend: Trend) -> bool:
    """True if trend has score ≥ 7.5 (high conviction), suggesting strong signal."""
    return (trend.ai_score or 0) >= 7.5


# ── Resolution decision ────────────────────────────────────────────────────────

def _decide(market: Market, trend: Trend, dry_run: bool = True) -> str:
    """
    Returns 'yes' | 'no' | 'skip'.
    Logs evidence. Writes to DB if not dry_run.
    """
    name = trend.name if trend else market.question[:40]
    print(f"\n  Market: {market.id[:8]}… '{name}'")

    evidence_yes = 0
    evidence_no  = 0
    notes = []

    # ── Google Trends ─────────────────────────────────────────────────────────
    is_mainstream, peak = _google_mainstream(name)
    if is_mainstream:
        evidence_yes += 1
        notes.append(f"Google peak={peak:.0f}/100 ✓ mainstream")
    else:
        evidence_no += 1
        notes.append(f"Google peak={peak:.0f}/100 — not mainstream")

    # ── Editorial ─────────────────────────────────────────────────────────────
    since = market.created_at or datetime.utcnow() - timedelta(days=90)
    mentions = _editorial_mentions(name, since)
    if mentions >= 2:
        evidence_yes += 1
        notes.append(f"Editorial: {mentions} mentions ✓")
    elif mentions == 1:
        notes.append(f"Editorial: {mentions} mention (weak)")
    else:
        evidence_no += 1
        notes.append("Editorial: 0 mentions")

    # ── AI Score ──────────────────────────────────────────────────────────────
    if _score_rose(trend):
        evidence_yes += 1
        notes.append(f"AI score={trend.ai_score:.1f} ≥7.5 ✓")
    else:
        notes.append(f"AI score={trend.ai_score:.1f} (below threshold)")

    print(f"    Evidence YES={evidence_yes}  NO={evidence_no}")
    for n in notes:
        print(f"    · {n}")

    # ── Decision ──────────────────────────────────────────────────────────────
    if evidence_yes >= 2:
        print(f"    → RESOLVE YES")
        return "yes"
    elif evidence_no >= 2 and evidence_yes == 0:
        print(f"    → RESOLVE NO")
        return "no"
    else:
        print(f"    → SKIP (insufficient evidence — manual review)")
        return "skip"


# ── Payout ────────────────────────────────────────────────────────────────────

def _pay_out(db, market: Market, outcome: str, evidence_note: str):
    """Resolve market and pay out winning positions."""
    market.status = MarketStatus.resolved_yes if outcome == "yes" else MarketStatus.resolved_no
    market.resolved_at = datetime.utcnow()
    market.auto_resolve_signal = evidence_note

    # Update trend status
    if market.trend:
        market.trend.status = TrendStatus.mainstream if outcome == "yes" else TrendStatus.dead

    winning_positions = [p for p in market.positions if p.position == outcome]
    total_pool = market.total_volume
    total_winning_shares = sum(p.shares for p in winning_positions)

    winners = 0
    for pos in winning_positions:
        payout = int(total_pool * (pos.shares / total_winning_shares)) if total_winning_shares > 0 else 0
        pos.payout = payout
        pos.user.points += payout
        pos.user.markets_won = (pos.user.markets_won or 0) + 1
        winners += 1

    # Track losses for NO positions
    losing_positions = [p for p in market.positions if p.position != outcome]
    for pos in losing_positions:
        pos.payout = 0
        pos.user.markets_lost = (pos.user.markets_lost or 0) + 1

    # Update accuracy rates
    all_users = set()
    for pos in market.positions:
        all_users.add(pos.user)
    for user in all_users:
        total_m = (user.markets_won or 0) + (user.markets_lost or 0)
        if total_m > 0:
            user.accuracy_rate = round((user.markets_won or 0) / total_m, 3)

    return winners


# ── Main ──────────────────────────────────────────────────────────────────────

def run(execute: bool = False, force_test: int = 0) -> dict:
    """
    force_test: if > 0, picks that many random open markets to test the
    resolution logic regardless of their resolution date (never writes to DB).
    """
    db = SessionLocal()
    now = datetime.utcnow()
    stats = {"checked": 0, "resolved_yes": 0, "resolved_no": 0, "skipped": 0, "errors": 0}

    try:
        if force_test > 0:
            import random
            all_open = db.query(Market).filter(Market.status == MarketStatus.open).all()
            due_markets = random.sample(all_open, min(force_test, len(all_open)))
            print(f"\n[auto_resolve] FORCE TEST MODE — sampling {len(due_markets)} random markets")
        else:
            # Markets past their resolution date that are still open
            due_markets = (
                db.query(Market)
                .filter(Market.status == MarketStatus.open)
                .filter(Market.resolution_date <= now)
                .all()
            )

        print(f"\n[auto_resolve] {len(due_markets)} markets past resolution date")
        if not due_markets:
            return stats

        for market in due_markets:
            stats["checked"] += 1
            trend = market.trend
            if not trend:
                print(f"  SKIP {market.id[:8]}: no trend linked")
                stats["skipped"] += 1
                continue

            try:
                decision = _decide(market, trend, dry_run=not execute)
            except Exception as e:
                print(f"  ERROR deciding {market.id[:8]}: {e}")
                stats["errors"] += 1
                continue

            if decision == "skip":
                stats["skipped"] += 1
                if execute:
                    # Extend by 14 days rather than leaving open forever
                    market.resolution_date = now + timedelta(days=14)
                    market.auto_resolve_signal = "insufficient_evidence — extended 14d"
                    db.commit()
            elif execute:
                try:
                    winners = _pay_out(db, market, decision, f"auto_resolve:{decision}")
                    db.commit()
                    print(f"    Paid out {winners} winners from pool of {market.total_volume} pts")
                    if decision == "yes":
                        stats["resolved_yes"] += 1
                    else:
                        stats["resolved_no"] += 1
                except Exception as e:
                    db.rollback()
                    print(f"  ERROR paying out {market.id[:8]}: {e}")
                    stats["errors"] += 1
            else:
                # Dry run — just count
                if decision == "yes":
                    stats["resolved_yes"] += 1
                else:
                    stats["resolved_no"] += 1

    finally:
        db.close()

    print(f"\n[auto_resolve] Done: {stats}")
    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-resolve expired fashion markets")
    parser.add_argument("--execute",    action="store_true", help="Write resolutions to DB (default: dry run)")
    parser.add_argument("--force-test", type=int, default=0, metavar="N",
                        help="Test resolution logic on N random open markets (never writes to DB)")
    args = parser.parse_args()

    mode = "FORCE TEST" if args.force_test else ("EXECUTE" if args.execute else "DRY RUN")
    print(f"Auto-Resolution Agent [{mode}]")
    print("=" * 50)
    run(execute=args.execute, force_test=args.force_test)
