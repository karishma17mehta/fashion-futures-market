"""
Trend Report API
================
Serves the forward-looking trend report — the buying-team deliverable built on
top of the signal engine. See agents/trend_report.py for generation.

Endpoints:
  GET  /reports/latest    — the most recently generated report (cached JSON)
  POST /reports/generate  — rebuild the report from current top signals
"""
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

_REPORT_FILE = Path(__file__).resolve().parent.parent.parent.parent / "data" / "trend_report.json"


@router.get("/latest")
def latest_report():
    """Return the most recently generated trend report."""
    if not _REPORT_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="No report generated yet. Run: python -m agents.trend_report",
        )
    return json.loads(_REPORT_FILE.read_text())


@router.post("/generate")
def generate(
    limit: int = Query(default=8, ge=3, le=20),
    min_score: float = Query(default=5.0, ge=0, le=10),
):
    """Rebuild the report from the current top signals. Calls Claude once."""
    from agents.trend_report import generate_report

    try:
        report = generate_report(limit=limit, min_score=min_score)
    except Exception as exc:  # surface generation errors cleanly to the client
        raise HTTPException(status_code=500, detail=str(exc))
    return report
