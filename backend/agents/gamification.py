"""
Gamification Engine
===================
Awards XP, tracks streaks, and grants badges based on user activity.

XP Actions:
  trade_placed        +10 XP per trade
  early_adopter       +50 XP for being in top 10% of traders on a trend
  market_won          +100 XP per correct prediction
  hot_streak          +25 XP bonus per day of a 3+ day streak
  cross_platform_call +30 XP for betting on a trend before it gets cross-platform confirmed
  high_score_call     +40 XP for betting on a trend that later hits score ≥ 8.5

Badges:
  trend_hunter        First trade on 3+ emerging trends
  oracle              70%+ accuracy after 10+ trades
  early_adopter       Traded a trend before it went cross-platform confirmed
  hot_streak          7+ day active streak
  whale               Single trade of 200+ points
  contrarian          Won a NO market that was priced >70% YES
  fashion_week        Traded 5+ Editorial trends
  data_driven         Traded 5+ trends from different sources

Rank thresholds:
  novice     0 – 499 XP
  forecaster 500 – 1999 XP
  oracle     2000 – 4999 XP
  legend     5000+ XP

Usage:
    python -m agents.gamification          # dry run
    python -m agents.gamification --execute
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
load_dotenv(_BACKEND / ".env", override=False)

from db.session import SessionLocal
from db.models import User, Position, Market, MarketStatus, Trend, UserActivity, UserBadge, UserRank


# ── XP thresholds → rank ──────────────────────────────────────────────────────

RANK_THRESHOLDS = [
    (5000, UserRank.legend),
    (2000, UserRank.oracle),
    (500,  UserRank.forecaster),
    (0,    UserRank.novice),
]

def _rank_for_xp(xp: int) -> UserRank:
    for threshold, rank in RANK_THRESHOLDS:
        if xp >= threshold:
            return rank
    return UserRank.novice


# ── Activity logging ──────────────────────────────────────────────────────────

def _log_activity(db, user: User, action: str, xp: int, detail: str = "", execute: bool = True):
    if execute:
        db.add(UserActivity(
            id=str(uuid.uuid4()),
            user_id=user.id,
            action=action,
            xp_earned=xp,
            detail=detail,
        ))
        user.xp = (user.xp or 0) + xp
    print(f"    +{xp} XP [{action}] {detail}")


def _grant_badge(db, user: User, slug: str, name: str, desc: str, execute: bool = True) -> bool:
    """Returns True if badge was newly granted (not already held)."""
    if execute:
        existing = db.query(UserBadge).filter(
            UserBadge.user_id == user.id,
            UserBadge.badge_slug == slug,
        ).first()
        if existing:
            return False
        db.add(UserBadge(
            id=str(uuid.uuid4()),
            user_id=user.id,
            badge_slug=slug,
            badge_name=name,
            badge_desc=desc,
        ))
    print(f"    🏅 Badge: {name} — {desc}")
    return True


# ── Streak tracking ───────────────────────────────────────────────────────────

def _update_streak(db, user: User, execute: bool = True):
    """Update streak_days and award streak bonus XP if applicable."""
    now = datetime.utcnow()
    last = user.last_active

    if last is None:
        new_streak = 1
    else:
        delta = (now.date() - last.date()).days
        if delta == 0:
            return  # Already recorded today
        elif delta == 1:
            new_streak = (user.streak_days or 0) + 1
        else:
            new_streak = 1  # Streak broken

    if execute:
        user.streak_days = new_streak
        user.last_active = now

    # Bonus XP for streaks
    if new_streak >= 3:
        _log_activity(db, user, "hot_streak", 25, f"{new_streak}-day streak", execute)

    if new_streak == 7:
        _grant_badge(db, user, "hot_streak", "Hot Streak", "7 consecutive days active", execute)

    print(f"    Streak: {new_streak} days")


# ── Per-trade XP ──────────────────────────────────────────────────────────────

def _award_trade_xp(db, user: User, position: Position, execute: bool = True):
    """Award XP for placing a trade and check for early-adopter bonus."""
    trend = position.market.trend if position.market else None
    trend_name = trend.name if trend else "unknown"

    # Base trade XP
    _log_activity(db, user, "trade_placed", 10, f"{position.position.upper()} on '{trend_name}'", execute)

    # Whale badge: single trade ≥ 200 pts
    if position.cost >= 200:
        _grant_badge(db, user, "whale", "Whale", "Single trade of 200+ points", execute)

    # Early adopter: traded an emerging trend
    if trend and trend.status and str(trend.status) == "emerging":
        _log_activity(db, user, "early_adopter", 50, f"Emerging call on '{trend_name}'", execute)

    # Cross-platform bonus: trend later confirmed on multiple platforms
    if trend and (trend.platform_count or 1) >= 2:
        # Check if this trade was placed before cross-platform confirmation
        # (confirmed_sources was empty when trade was placed — approximate with trend creation date)
        if position.created_at and trend.score_updated_at:
            if position.created_at < trend.score_updated_at:
                _log_activity(db, user, "cross_platform_call", 30,
                              f"Called '{trend_name}' before cross-platform confirm", execute)


# ── Market resolution awards ──────────────────────────────────────────────────

def _award_resolution_xp(db, user: User, position: Position, execute: bool = True):
    """Called after a market resolves. Awards win XP + badge checks."""
    market = position.market
    trend = market.trend if market else None
    trend_name = trend.name if trend else "unknown"
    outcome = str(market.status)

    won = (
        (outcome == "resolved_yes" and position.position == "yes") or
        (outcome == "resolved_no"  and position.position == "no")
    )

    if won:
        _log_activity(db, user, "market_won", 100, f"Correct on '{trend_name}'", execute)

        # Contrarian badge: won a NO bet when YES was priced >70%
        if position.position == "no" and market.yes_price and market.yes_price > 0.70:
            _grant_badge(db, user, "contrarian", "Contrarian",
                         "Won a NO market priced >70% YES", execute)

        # High-score-call bonus: trend hit ≥ 8.5 and they called it
        if trend and (trend.ai_score or 0) >= 8.5:
            _log_activity(db, user, "high_score_call", 40, f"'{trend_name}' hit {trend.ai_score:.1f}", execute)


# ── Global badge checks ───────────────────────────────────────────────────────

def _check_global_badges(db, user: User, all_positions: list, execute: bool = True):
    """Check collection-based badges that require looking at all positions."""

    # Oracle: 70%+ accuracy after 10+ trades
    total = (user.markets_won or 0) + (user.markets_lost or 0)
    if total >= 10 and (user.accuracy_rate or 0) >= 0.70:
        _grant_badge(db, user, "oracle", "Oracle", "70%+ accuracy after 10+ trades", execute)

    # Trend hunter: first trade on 3+ emerging trends
    emerging_trends = set()
    for p in all_positions:
        if p.market and p.market.trend:
            t = p.market.trend
            if str(t.status) == "emerging":
                emerging_trends.add(t.id)
    if len(emerging_trends) >= 3:
        _grant_badge(db, user, "trend_hunter", "Trend Hunter", "Traded 3+ emerging trends", execute)

    # Fashion week: 5+ editorial trades
    editorial_trades = [p for p in all_positions
                        if p.market and p.market.trend and
                        p.market.trend.source == "editorial_rss"]
    if len(editorial_trades) >= 5:
        _grant_badge(db, user, "fashion_week", "Fashion Week",
                     "Traded 5+ editorial-sourced trends", execute)

    # Data-driven: trades across 5+ different sources
    sources = set()
    for p in all_positions:
        if p.market and p.market.trend and p.market.trend.source:
            sources.add(p.market.trend.source)
    if len(sources) >= 5:
        _grant_badge(db, user, "data_driven", "Data-Driven",
                     "Traded trends from 5+ different sources", execute)


# ── Main ──────────────────────────────────────────────────────────────────────

def run(execute: bool = False) -> dict:
    db = SessionLocal()
    stats = {"users": 0, "xp_awarded": 0, "badges": 0, "rank_ups": 0}

    try:
        users = db.query(User).all()
        print(f"\n[gamification] Processing {len(users)} users...")

        for user in users:
            stats["users"] += 1
            xp_before = user.xp or 0
            print(f"\n  User: {user.username} (XP={xp_before}, streak={user.streak_days})")

            # Streak update
            _update_streak(db, user, execute)

            # Per-trade XP for recent positions (last 7 days)
            recent_cutoff = datetime.utcnow() - timedelta(days=7)
            recent_positions = [
                p for p in user.positions
                if p.created_at and p.created_at >= recent_cutoff
            ]
            for pos in recent_positions:
                _award_trade_xp(db, user, pos, execute)

            # Resolution XP for recently resolved markets
            resolved_positions = [
                p for p in user.positions
                if p.market and p.market.status in (MarketStatus.resolved_yes, MarketStatus.resolved_no)
                and p.payout is not None
            ]
            for pos in resolved_positions:
                _award_resolution_xp(db, user, pos, execute)

            # Global badge checks
            badges_before = len(user.badges) if execute else 0
            _check_global_badges(db, user, user.positions, execute)

            # Rank update
            new_rank = _rank_for_xp(user.xp or 0)
            if execute and new_rank != user.rank:
                print(f"    🎖 Rank up: {user.rank} → {new_rank}")
                user.rank = new_rank
                stats["rank_ups"] += 1

            xp_gained = (user.xp or 0) - xp_before
            stats["xp_awarded"] += xp_gained

        if execute:
            db.commit()
            print(f"\n[gamification] Committed to DB")
        else:
            print(f"\n[gamification] DRY RUN — no changes written")

    except Exception as e:
        db.rollback()
        print(f"[gamification] ERROR: {e}")
        raise
    finally:
        db.close()

    print(f"[gamification] Stats: {stats}")
    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fashion Futures gamification engine")
    parser.add_argument("--execute", action="store_true", help="Write to DB (default: dry run)")
    args = parser.parse_args()

    mode = "EXECUTE" if args.execute else "DRY RUN"
    print(f"Gamification Engine [{mode}]")
    print("=" * 50)
    run(execute=args.execute)
