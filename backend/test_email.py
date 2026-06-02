"""Quick smoke test — sends a test email using your .env SMTP config."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv(".env", override=True)

from agents.alert_dispatcher import _send_email
import os

recipient = os.getenv("DIGEST_EMAIL")
if not recipient:
    print("Set DIGEST_EMAIL in .env first")
    sys.exit(1)

print(f"Sending test email to {recipient}...")
ok = _send_email(
    to=recipient,
    subject="Fashion Futures — Email Test",
    body="""
<html><body style="font-family:sans-serif;background:#080808;color:#f5f0eb;padding:32px">
  <h2 style="font-family:Georgia,serif;font-weight:300;color:#d4a853">Email working ✓</h2>
  <p style="color:rgba(245,240,235,0.7)">
    Your Fashion Futures alert system is configured correctly.<br>
    You'll receive weekly digests and trend alerts here.
  </p>
</body></html>
""",
)

if ok:
    print("✓ Email sent successfully")
else:
    print("✗ Email failed — check SMTP_ values in .env")
