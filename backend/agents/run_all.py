"""
Agent Orchestrator
==================
Runs all agents in the correct order. Called by cron weekly.

Order:
  1. Pipeline     — scrape fresh signals, score, write new trends
  2. Score Decay  — decay stale scores, apply cross-platform boosts
  3. Auto-Resolve — resolve expired markets with real-world evidence
  4. Digest       — compile weekly summary, send email
  5. Alerts       — fire user notifications

Usage:
    python -m agents.run_all                  # full weekly run
    python -m agents.run_all --skip-scrape    # skip pipeline (use existing data)
    python -m agents.run_all --dry-run        # no DB writes, no emails
"""
import sys
import argparse
from datetime import datetime
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent.parent
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

import os as _os
from dotenv import load_dotenv
# Preserve a DATABASE_URL passed on the command line (e.g. pointing at the
# cloud DB) so the local .env value doesn't clobber it. In Railway there is no
# .env file, so the platform-provided env vars are used as-is.
_cli_db = _os.environ.get("DATABASE_URL")
load_dotenv(_BACKEND / ".env", override=False)
if _cli_db:
    _os.environ["DATABASE_URL"] = _cli_db


def main():
    parser = argparse.ArgumentParser(description="Fashion Futures weekly agent run")
    parser.add_argument("--skip-scrape", action="store_true", help="Skip the scraper pipeline")
    parser.add_argument("--dry-run",     action="store_true", help="No DB writes, no emails")
    parser.add_argument("--send-email",  action="store_true", help="Send digest + alert emails")
    args = parser.parse_args()

    start = datetime.utcnow()
    print(f"\n{'='*60}")
    print(f"  Fashion Futures — Weekly Agent Run")
    print(f"  {start.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"  dry_run={args.dry_run}  skip_scrape={args.skip_scrape}")
    print(f"{'='*60}")

    # ── Step 1: Scraper pipeline ──────────────────────────────────────────────
    if not args.skip_scrape:
        print("\n[1/5] Running scraper pipeline...")
        try:
            from scrapers.pipeline import run_pipeline
            run_pipeline()
        except Exception as e:
            print(f"  [ERROR] Pipeline failed: {e}")
    else:
        print("\n[1/5] Skipping scraper pipeline (--skip-scrape)")

    # ── Step 2: Score decay + cross-platform boost ────────────────────────────
    print("\n[2/5] Score decay + cross-platform boost...")
    try:
        from agents.score_decay import run as decay_run
        stats = decay_run(execute=not args.dry_run)
        print(f"  Decayed: {stats['decayed']}  Boosted: {stats['cross_platform']}  Snapshots: {stats['snapshots']}")
    except Exception as e:
        print(f"  [ERROR] Score decay failed: {e}")

    # ── Step 3: Auto-resolve expired markets ──────────────────────────────────
    print("\n[3/5] Auto-resolving expired markets...")
    try:
        from agents.auto_resolve import run as resolve_run
        stats = resolve_run(execute=not args.dry_run)
        print(f"  YES: {stats['resolved_yes']}  NO: {stats['resolved_no']}  Skipped: {stats['skipped']}")
    except Exception as e:
        print(f"  [ERROR] Auto-resolve failed: {e}")

    # ── Step 4: Weekly digest ─────────────────────────────────────────────────
    print("\n[4/5] Generating weekly digest...")
    try:
        from agents.weekly_digest import run as digest_run
        digest = digest_run(send_email=args.send_email and not args.dry_run)
        print(f"  New: {digest['stats']['new_this_week']}  Resolved: {digest['stats']['markets_resolved']}")
    except Exception as e:
        print(f"  [ERROR] Digest failed: {e}")

    # ── Step 5: Gamification ──────────────────────────────────────────────────
    print("\n[5/6] Running gamification engine...")
    try:
        from agents.gamification import run as gamify_run
        stats = gamify_run(execute=not args.dry_run)
        print(f"  XP awarded: {stats['xp_awarded']}  Badges: {stats['badges']}  Rank-ups: {stats['rank_ups']}")
    except Exception as e:
        print(f"  [ERROR] Gamification failed: {e}")

    # ── Step 6: Alert dispatcher ──────────────────────────────────────────────
    print("\n[6/6] Dispatching alerts...")
    try:
        if not args.dry_run:
            from agents.alert_dispatcher import run as alert_run
            stats = alert_run()
            print(f"  Fired: {stats['fired']}  Skipped: {stats['skipped']}")
        else:
            print("  Skipped (dry run)")
    except Exception as e:
        print(f"  [ERROR] Alerts failed: {e}")

    elapsed = (datetime.utcnow() - start).total_seconds()
    print(f"\n{'='*60}")
    print(f"  Weekly run complete in {elapsed:.0f}s")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
