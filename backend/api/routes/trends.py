from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

from db.session import get_db
from db.models import Trend, TrendStatus

router = APIRouter()


class TrendCreate(BaseModel):
    name: str
    description: str
    ai_score: float
    ai_thesis: str
    source: str
    signal_velocity: float


class TrendOut(BaseModel):
    id: str
    name: str
    description: str
    ai_score: float
    ai_thesis: str
    source: str
    signal_velocity: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/")
def list_trends(
    limit: int = 20,
    min_score: Optional[float] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Trend)
    if min_score is not None:
        query = query.filter(Trend.ai_score >= min_score)
    trends = query.order_by(Trend.ai_score.desc()).limit(limit).all()
    return {"trends": [TrendOut.from_orm(t) for t in trends], "total": len(trends)}


@router.get("/{trend_id}")
def get_trend(trend_id: str, db: Session = Depends(get_db)):
    trend = db.query(Trend).filter(Trend.id == trend_id).first()
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    return TrendOut.from_orm(trend)


@router.post("/", response_model=TrendOut, status_code=201)
def create_trend(data: TrendCreate, db: Session = Depends(get_db)):
    trend = Trend(
        id=str(uuid.uuid4()),
        **data.model_dump()
    )
    db.add(trend)
    db.commit()
    db.refresh(trend)
    return TrendOut.from_orm(trend)


@router.post("/scan")
def trigger_scan():
    # TODO: kick off background scraper job
    return {"status": "scan_queued"}
