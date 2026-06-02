"""
Alert Subscription API
=======================
Lets users create and manage trend alert subscriptions.

POST /alerts/              — create a new alert
GET  /alerts/{user_id}     — list user's alerts
DELETE /alerts/{alert_id}  — remove an alert
"""
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from db.session import get_db
from db.models import TrendAlert, User

router = APIRouter()


class AlertCreate(BaseModel):
    user_id:       str
    trend_name:    str          # e.g. "Ballet Core", "quiet luxury", or "*" for all
    min_score:     float = 7.0
    source_filter: Optional[str] = None   # e.g. "tiktok" — optional


class AlertOut(BaseModel):
    id:            str
    user_id:       str
    trend_name:    str
    min_score:     float
    source_filter: Optional[str]
    active:        bool
    last_fired:    Optional[datetime]
    created_at:    datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=AlertOut, status_code=201)
def create_alert(data: AlertCreate, db: Session = Depends(get_db)):
    """
    Subscribe to trend alerts.

    Examples:
      { "user_id": "...", "trend_name": "Ballet Core", "min_score": 7.0 }
      { "user_id": "...", "trend_name": "*", "min_score": 8.5, "source_filter": "tiktok" }
      { "user_id": "...", "trend_name": "quiet luxury", "min_score": 7.0 }
    """
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent duplicate alerts for the same term+score
    existing = db.query(TrendAlert).filter(
        TrendAlert.user_id == data.user_id,
        TrendAlert.trend_name == data.trend_name,
        TrendAlert.min_score == data.min_score,
        TrendAlert.active == True,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Alert already exists for this term and score threshold")

    alert = TrendAlert(
        id            = str(uuid.uuid4()),
        user_id       = data.user_id,
        trend_name    = data.trend_name,
        min_score     = data.min_score,
        source_filter = data.source_filter,
        active        = True,
        created_at    = datetime.utcnow(),
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return AlertOut.from_orm(alert)


@router.get("/{user_id}")
def list_alerts(user_id: str, db: Session = Depends(get_db)):
    """List all active alerts for a user."""
    alerts = db.query(TrendAlert).filter(
        TrendAlert.user_id == user_id,
        TrendAlert.active == True,
    ).order_by(TrendAlert.created_at.desc()).all()
    return {"alerts": [AlertOut.from_orm(a) for a in alerts]}


@router.delete("/{alert_id}", status_code=204)
def delete_alert(alert_id: str, db: Session = Depends(get_db)):
    """Deactivate an alert (soft delete)."""
    alert = db.query(TrendAlert).filter(TrendAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.active = False
    db.commit()


@router.patch("/{alert_id}/email")
def set_alert_email(alert_id: str, email: str, db: Session = Depends(get_db)):
    """Set the email address on the user associated with this alert."""
    alert = db.query(TrendAlert).filter(TrendAlert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.user.email = email
    db.commit()
    return {"email_set": email}
