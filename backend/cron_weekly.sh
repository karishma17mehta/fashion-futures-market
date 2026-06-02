#!/usr/bin/env bash
# Fashion Futures — Weekly Cron Script
# =====================================
# Add to crontab with:
#   crontab -e
#   0 6 * * 0 /Users/karishmamehta/Documents/fashion_tech/backend/cron_weekly.sh >> /tmp/fashion_futures_cron.log 2>&1
#
# Runs every Sunday at 6am local time.
# Logs to /tmp/fashion_futures_cron.log

set -e

BACKEND="/Users/karishmamehta/Documents/fashion_tech/backend"
VENV="$BACKEND/venv"
LOG="/tmp/fashion_futures_cron.log"

echo ""
echo "============================================================"
echo "  Fashion Futures Weekly Cron — $(date)"
echo "============================================================"

# Activate virtualenv
source "$VENV/bin/activate"

# Run the orchestrator
cd "$BACKEND"
python -m agents.run_all --send-email

echo "Cron complete — $(date)"
