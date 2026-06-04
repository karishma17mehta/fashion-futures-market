from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

from db.session import get_db
from db.models import User, Position, Market, Trend, UserActivity, UserBadge

router = APIRouter()


class UserCreate(BaseModel):
    username: str


class UserOut(BaseModel):
    id: str
    username: str
    points: int
    xp: int = 0
    streak_days: int = 0
    rank: str
    accuracy_rate: float
    total_trades: int
    markets_won: int = 0
    markets_lost: int = 0

    class Config:
        from_attributes = True


class BadgeOut(BaseModel):
    badge_slug: str
    badge_name: str
    badge_desc: Optional[str]
    earned_at: datetime

    class Config:
        from_attributes = True


class ActivityOut(BaseModel):
    action: str
    xp_earned: int
    detail: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PositionOut(BaseModel):
    id: str
    market_id: str
    position: str
    shares: float
    cost: int
    payout: int | None

    class Config:
        from_attributes = True


@router.post("/", response_model=UserOut, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Username taken")
    user = User(id=str(uuid.uuid4()), username=data.username)
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut.from_orm(user)


@router.get("/leaderboard")
def leaderboard(limit: int = 50, db: Session = Depends(get_db)):
    """Leaderboard ranked by XP (primary) then accuracy."""
    users = (
        db.query(User)
        .order_by(User.xp.desc(), User.accuracy_rate.desc(), User.total_trades.desc())
        .limit(limit)
        .all()
    )
    result = []
    for i, u in enumerate(users):
        badges = db.query(UserBadge).filter(UserBadge.user_id == u.id).all()
        result.append({
            **UserOut.from_orm(u).model_dump(),
            "rank_position": i + 1,
            "badge_count": len(badges),
            "badges": [b.badge_slug for b in badges],
        })
    return {"users": result}


@router.get("/by-username/{username}", response_model=UserOut)
def get_user_by_username(username: str, db: Session = Depends(get_db)):
    """Resolve a username to a user — lets a returning player resume their
    account from a new device (username-only auth, play-money game)."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut.from_orm(user)


@router.get("/{user_id}/badges")
def get_badges(user_id: str, db: Session = Depends(get_db)):
    """Return all badges earned by a user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    badges = db.query(UserBadge).filter(UserBadge.user_id == user_id)\
               .order_by(UserBadge.earned_at.desc()).all()
    return {"badges": [BadgeOut.from_orm(b) for b in badges]}


@router.get("/{user_id}/activity")
def get_activity(user_id: str, limit: int = 20, db: Session = Depends(get_db)):
    """Return recent XP activity log for a user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    activity = db.query(UserActivity).filter(UserActivity.user_id == user_id)\
                 .order_by(UserActivity.created_at.desc()).limit(limit).all()
    return {
        "activity": [ActivityOut.from_orm(a) for a in activity],
        "total_xp": user.xp or 0,
        "rank": str(user.rank),
        "streak": user.streak_days or 0,
    }


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut.from_orm(user)


@router.get("/{user_id}/positions")
def get_positions(user_id: str, db: Session = Depends(get_db)):
    """
    Returns positions enriched with market question, current prices,
    trend name, and current P&L calculation.
    """
    positions = db.query(Position).filter(Position.user_id == user_id).all()

    enriched = []
    for p in positions:
        market = db.query(Market).filter(Market.id == p.market_id).first()
        trend  = db.query(Trend).filter(Trend.id == market.trend_id).first() if market else None

        # Current value: shares × current price for this position
        if market:
            current_price = market.yes_price if p.position == "yes" else market.no_price
            current_value = round(p.shares * current_price * 100)  # in points
        else:
            current_price = 0.5
            current_value = p.cost  # can't calculate without market

        pnl = current_value - p.cost

        enriched.append({
            "id":            p.id,
            "market_id":     p.market_id,
            "position":      p.position,
            "shares":        round(p.shares, 4),
            "cost":          p.cost,
            "payout":        p.payout,
            "created_at":    p.created_at.isoformat() if p.created_at else None,
            # Market context
            "market_question":    market.question if market else "",
            "market_status":      market.status.value if market else "unknown",
            "market_yes_price":   round(market.yes_price, 4) if market else 0.5,
            "market_no_price":    round(market.no_price, 4) if market else 0.5,
            "resolution_date":    market.resolution_date.isoformat() if market else None,
            # Trend context
            "trend_id":    trend.id if trend else None,
            "trend_name":  trend.name if trend else "",
            "trend_score": trend.ai_score if trend else None,
            "trend_source": trend.source if trend else None,
            # P&L
            "current_price": round(current_price, 4),
            "current_value": current_value,
            "pnl":           pnl,
            "pnl_pct":       round(pnl / p.cost * 100, 1) if p.cost else 0,
        })

    # Summary stats
    total_invested = sum(p["cost"] for p in enriched if p["market_status"] == "open")
    total_current  = sum(p["current_value"] for p in enriched if p["market_status"] == "open")
    total_pnl      = total_current - total_invested

    return {
        "positions": enriched,
        "summary": {
            "total_positions": len(enriched),
            "open_positions":  sum(1 for p in enriched if p["market_status"] == "open"),
            "total_invested":  total_invested,
            "total_current":   total_current,
            "total_pnl":       total_pnl,
            "total_pnl_pct":   round(total_pnl / total_invested * 100, 1) if total_invested else 0,
        },
    }
