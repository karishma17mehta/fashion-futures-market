from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class Trend(BaseModel):
    id: str
    name: str
    description: str
    ai_score: float        # 1-10: novelty + velocity composite
    ai_thesis: str         # Claude's one-paragraph explanation
    source: str            # depop | reddit | tiktok | pinterest
    signal_velocity: float # % growth in mentions over 14 days
    created_at: str


@router.get("/")
def list_trends(limit: int = 20, min_score: Optional[float] = None):
    # TODO: fetch from DB
    return {"trends": [], "total": 0}


@router.get("/{trend_id}")
def get_trend(trend_id: str):
    # TODO: fetch from DB
    raise HTTPException(status_code=404, detail="Trend not found")


@router.post("/scan")
def trigger_scan():
    """Trigger the AI signal scraper to find new trends."""
    # TODO: kick off scraper job
    return {"status": "scan_queued"}
