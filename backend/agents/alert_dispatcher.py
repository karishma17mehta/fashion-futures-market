"""
Alert Dispatcher Agent
======================
Checks TrendAlerts against newly detected trends and fires notifications.

Currently supports:
  - Console output (always)
  - Email via SMTP (if SMTP_HOST + SMTP_FROM set in .env)

Alert triggers:
  - New trend detected matching user's watched name/keywords
  - Trend score crosses user's min_score threshold
  - Trend crosses from 'emerging' to 'active'

Usage:
    python -m agents.alert_dispatcher       # check and fire pending alerts
"""
import sys
import os
import smtplib
import uuid
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

_BACKEND = Path(__file__).resolve().parent.parent
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

from dotenv import load_dotenv
load_dotenv(_BACKEND / ".env", override=False)

from db.session import SessionLocal
from db.models import Trend, TrendAlert, TrendStatus


# ── Email ─────────────────────────────────────────────────────────────────────

def _send_email(to: str, subject: str, body: str) -> bool:
    host     = os.getenv("SMTP_HOST")
    port     = int(os.getenv("SMTP_PORT", "587"))
    user     = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    from_    = os.getenv("SMTP_FROM", user)

    if not host or not user:
        print(f"  [email] SMTP not configured — would send to {to}: {subject}")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = from_
        msg["To"]      = to
        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP(host, port) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            smtp.sendmail(from_, to, msg.as_string())
        print(f"  [email] Sent to {to}: {subject}")
        return True
    except Exception as e:
        print(f"  [email] Failed to {to}: {e}")
        return False


def _email_body(trend: Trend, alert: TrendAlert) -> str:
    return f"""
<html><body style="font-family:sans-serif;background:#080808;color:#f5f0eb;padding:32px">
  <h2 style="font-family:Georgia,serif;font-weight:300;color:#d4a853">
    Fashion Futures Signal Alert
  </h2>
  <p style="color:rgba(245,240,235,0.7)">
    A trend you're watching has crossed your alert threshold.
  </p>
  <div style="border-left:2px solid #d4a853;padding:16px 24px;margin:24px 0;background:#0f0f0f">
    <p style="font-family:Georgia,serif;font-size:22px;margin:0 0 8px">{trend.name}</p>
    <p style="color:rgba(245,240,235,0.5);font-size:12px;margin:0">
      Score: <strong style="color:#d4a853">{trend.ai_score:.1f}/10</strong> ·
      Source: {trend.source} ·
      Status: {trend.status}
    </p>
    <p style="color:rgba(245,240,235,0.7);font-size:14px;margin:16px 0 0;line-height:1.6">
      {trend.ai_thesis or trend.description or ""}
    </p>
  </div>
  <a href="http://localhost:3000/trends/{trend.id}"
     style="display:inline-block;padding:10px 20px;background:#d4a853;color:#080808;
            text-decoration:none;font-size:11px;letter-spacing:0.15em;text-transform:uppercase">
    View Trend →
  </a>
  <p style="color:rgba(245,240,235,0.25);font-size:11px;margin-top:32px">
    You're receiving this because you set an alert for "{alert.trend_name}"
    with min score {alert.min_score}. Manage alerts at fashionfutures.io/alerts.
  </p>
</body></html>
"""


# ── Name matching ──────────────────────────────────────────────────────────────

def _alert_matches(alert: TrendAlert, trend: Trend) -> bool:
    """True if the trend name matches the alert's watch pattern."""
    watch = alert.trend_name.lower().strip()
    name  = trend.name.lower()
    return watch in name or name in watch or watch == "*"  # * = all trends


# ── Main ──────────────────────────────────────────────────────────────────────

def run() -> dict:
    db = SessionLocal()
    stats = {"alerts_checked": 0, "fired": 0, "skipped": 0}
    now = datetime.utcnow()
    cooldown = timedelta(hours=24)  # don't re-fire the same alert within 24h

    try:
        alerts = db.query(TrendAlert).filter(TrendAlert.active == True).all()
        print(f"\n[alert_dispatcher] {len(alerts)} active alerts")

        # Get recent high-scoring trends (last 7 days)
        cutoff = now - timedelta(days=7)
        recent_trends = db.query(Trend).filter(Trend.created_at >= cutoff).all()
        all_trends    = db.query(Trend).filter(Trend.status != "dead").all()

        for alert in alerts:
            stats["alerts_checked"] += 1

            # Cooldown check
            if alert.last_fired and (now - alert.last_fired) < cooldown:
                stats["skipped"] += 1
                continue

            # Source filter
            search_pool = all_trends
            if alert.source_filter:
                search_pool = [t for t in all_trends if t.source == alert.source_filter]

            # Find matching trends above threshold
            matches = [
                t for t in search_pool
                if _alert_matches(alert, t) and (t.ai_score or 0) >= alert.min_score
            ]

            if not matches:
                continue

            for trend in matches[:3]:  # cap at 3 per alert to avoid spam
                user = alert.user
                print(f"  FIRE: '{trend.name}' score={trend.ai_score:.1f} → user={user.username}")

                # Email if user has one
                if user.email:
                    subj = f"Fashion Futures: '{trend.name}' crossed score {alert.min_score}"
                    body = _email_body(trend, alert)
                    _send_email(user.email, subj, body)

                stats["fired"] += 1

            alert.last_fired = now

        db.commit()

    finally:
        db.close()

    print(f"\n[alert_dispatcher] Done: {stats}")
    return stats


if __name__ == "__main__":
    run()
