"""
Brand Intelligence API
=======================
Public-facing API for brands and retailers to query trend signals.
Designed for integration into buying systems, trend dashboards, and
internal tools.

Endpoints:
  GET /signals/top           — top signals by score with optional filters
  GET /signals/cross-platform — trends confirmed on 2+ platforms
  GET /signals/by-source/{source} — all signals from a specific platform
  GET /signals/velocity       — ranked by signal_velocity (fastest moving)
  GET /signals/digest         — latest weekly digest JSON
  POST /signals/webhook       — register a webhook URL for new trend alerts
"""
import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from db.session import get_db
from db.models import Trend, TrendStatus

router = APIRouter()

_DIGEST_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "weekly_digest.json"

# ── Output schemas ────────────────────────────────────────────────────────────

class SignalOut(BaseModel):
    id:               str
    name:             str
    description:      Optional[str]
    ai_score:         float
    signal_velocity:  Optional[float]
    source:           Optional[str]
    status:           str
    platform_count:   Optional[int]
    confirmed_sources: Optional[str]
    created_at:       datetime
    ai_thesis:        Optional[str] = None  # only included when detail=true

    class Config:
        from_attributes = True


# ── Helpers ───────────────────────────────────────────────────────────────────

def _to_out(t: Trend, include_thesis: bool = False) -> dict:
    out = {
        "id":               t.id,
        "name":             t.name,
        "description":      t.description,
        "ai_score":         t.ai_score or 0.0,
        "signal_velocity":  t.signal_velocity,
        "source":           t.source,
        "status":           t.status.value if t.status else "emerging",
        "platform_count":   t.platform_count or 1,
        "confirmed_sources": t.confirmed_sources,
        "created_at":       t.created_at,
    }
    if include_thesis:
        out["ai_thesis"] = t.ai_thesis
    return out


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/top")
def top_signals(
    limit:         int            = Query(default=20, le=200),
    min_score:     float          = Query(default=5.0),
    source:        Optional[str]  = Query(default=None, description="tiktok|pinterest|reddit|editorial_rss|google_trends"),
    status:        Optional[str]  = Query(default=None, description="emerging|active|mainstream"),
    cross_platform_only: bool     = Query(default=False),
    include_thesis: bool          = Query(default=False),
    db:            Session        = Depends(get_db),
):
    """
    Top fashion trend signals by AI confidence score.

    Filter by source platform, minimum score, or cross-platform confirmation.
    Use include_thesis=true to get the AI narrative for each trend.

    Perfect for: buying team dashboards, weekly trend briefs, product planning tools.
    """
    query = db.query(Trend).filter(
        Trend.ai_score >= min_score,
        Trend.status != TrendStatus.dead,
    )
    if source:
        query = query.filter(Trend.source.contains(source))
    if status:
        query = query.filter(Trend.status == status)
    if cross_platform_only:
        query = query.filter(Trend.platform_count >= 2)

    trends = query.order_by(Trend.ai_score.desc()).limit(limit).all()

    return {
        "count": len(trends),
        "filters": {
            "min_score": min_score,
            "source": source,
            "status": status,
            "cross_platform_only": cross_platform_only,
        },
        "signals": [_to_out(t, include_thesis) for t in trends],
    }


@router.get("/cross-platform")
def cross_platform_confirmed(
    limit: int = Query(default=20, le=100),
    min_platforms: int = Query(default=2),
    db: Session = Depends(get_db),
):
    """
    Trends confirmed on 2 or more independent platforms.
    These are the strongest signals — the crowd intelligence agrees.

    A trend appearing on TikTok AND Pinterest AND Reddit simultaneously
    has a dramatically higher breakout probability than single-source signals.
    """
    trends = (
        db.query(Trend)
        .filter(Trend.platform_count >= min_platforms)
        .filter(Trend.status != TrendStatus.dead)
        .order_by(Trend.ai_score.desc())
        .limit(limit)
        .all()
    )
    return {
        "count": len(trends),
        "min_platforms": min_platforms,
        "signals": [_to_out(t, include_thesis=True) for t in trends],
    }


@router.get("/by-source/{source}")
def signals_by_source(
    source: str,
    limit: int = Query(default=30, le=100),
    min_score: float = Query(default=4.0),
    db: Session = Depends(get_db),
):
    """
    All signals from a specific platform.

    Sources: tiktok, pinterest, pinterest_predicts_2026, reddit,
             editorial_rss, google_trends, trend_intelligence
    """
    trends = (
        db.query(Trend)
        .filter(Trend.source.contains(source))
        .filter(Trend.ai_score >= min_score)
        .filter(Trend.status != TrendStatus.dead)
        .order_by(Trend.ai_score.desc())
        .limit(limit)
        .all()
    )
    return {
        "source": source,
        "count": len(trends),
        "signals": [_to_out(t) for t in trends],
    }


@router.get("/velocity")
def top_velocity(
    limit: int = Query(default=20, le=100),
    min_velocity: float = Query(default=10.0, description="Minimum signal_velocity %"),
    db: Session = Depends(get_db),
):
    """
    Fastest-moving trends right now, ranked by signal velocity.

    High velocity = the trend is accelerating, not just popular.
    Use this to catch breakout trends before they peak.
    """
    trends = (
        db.query(Trend)
        .filter(Trend.signal_velocity >= min_velocity)
        .filter(Trend.status != TrendStatus.dead)
        .order_by(Trend.signal_velocity.desc())
        .limit(limit)
        .all()
    )
    return {
        "count": len(trends),
        "min_velocity": min_velocity,
        "signals": [_to_out(t) for t in trends],
    }


@router.get("/digest")
def weekly_digest():
    """
    Latest weekly digest: top movers, new trends, resolved markets.
    Generated every Sunday by the digest agent.
    """
    if not _DIGEST_FILE.exists():
        raise HTTPException(status_code=404, detail="No digest available yet. Run: python -m agents.weekly_digest")
    return json.loads(_DIGEST_FILE.read_text())


@router.get("/score-history/{trend_id}")
def score_history(
    trend_id: str,
    limit: int = Query(default=12, le=52),
    db: Session = Depends(get_db),
):
    """
    Weekly score history for a trend. Use to power sparkline charts.
    Returns chronological list of (recorded_at, score, velocity).
    """
    from db.models import TrendScoreHistory
    history = (
        db.query(TrendScoreHistory)
        .filter(TrendScoreHistory.trend_id == trend_id)
        .order_by(TrendScoreHistory.recorded_at.desc())
        .limit(limit)
        .all()
    )
    return {
        "trend_id": trend_id,
        "history": [
            {
                "recorded_at": h.recorded_at.isoformat(),
                "score": h.score,
                "velocity": h.velocity,
            }
            for h in reversed(history)  # chronological order
        ],
    }
