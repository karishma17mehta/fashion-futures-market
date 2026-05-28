from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Literal
from datetime import datetime
import uuid
import math

from db.session import get_db
from db.models import Market, Position, User, MarketStatus

router = APIRouter()


class MarketCreate(BaseModel):
    trend_id: str
    question: str
    resolution_date: datetime
    resolution_criteria: str


class MarketOut(BaseModel):
    id: str
    trend_id: str
    question: str
    resolution_date: datetime
    resolution_criteria: str
    yes_price: float
    no_price: float
    total_volume: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class TradeRequest(BaseModel):
    user_id: str
    position: Literal["yes", "no"]
    amount: int


def lmsr_cost(b: float, yes_shares: float, no_shares: float) -> float:
    return b * math.log(math.exp(yes_shares / b) + math.exp(no_shares / b))


def lmsr_price(b: float, shares_for: float, shares_against: float) -> float:
    """Current marginal price for a position."""
    return math.exp(shares_for / b) / (math.exp(shares_for / b) + math.exp(shares_against / b))


@router.get("/")
def list_markets(status: str = "open", db: Session = Depends(get_db)):
    markets = db.query(Market).filter(Market.status == status).all()
    return {"markets": [MarketOut.from_orm(m) for m in markets], "total": len(markets)}


@router.get("/{market_id}")
def get_market(market_id: str, db: Session = Depends(get_db)):
    market = db.query(Market).filter(Market.id == market_id).first()
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    return MarketOut.from_orm(market)


@router.post("/", response_model=MarketOut, status_code=201)
def create_market(data: MarketCreate, db: Session = Depends(get_db)):
    market = Market(id=str(uuid.uuid4()), **data.model_dump())
    db.add(market)
    db.commit()
    db.refresh(market)
    return MarketOut.from_orm(market)


@router.post("/{market_id}/trade")
def place_trade(market_id: str, trade: TradeRequest, db: Session = Depends(get_db)):
    market = db.query(Market).filter(Market.id == market_id).first()
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    if market.status != MarketStatus.open:
        raise HTTPException(status_code=400, detail="Market is not open")

    user = db.query(User).filter(User.id == trade.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.points < trade.amount:
        raise HTTPException(status_code=400, detail="Insufficient points")

    # LMSR: calculate shares received for the cost (amount of points)
    b = market.liquidity_param
    existing_yes = sum(p.shares for p in market.positions if p.position == "yes")
    existing_no = sum(p.shares for p in market.positions if p.position == "no")

    cost_before = lmsr_cost(b, existing_yes, existing_no)

    # Binary search to find how many shares `amount` points buys
    shares = trade.amount / lmsr_price(b, existing_yes, existing_no)
    if trade.position == "yes":
        cost_after = lmsr_cost(b, existing_yes + shares, existing_no)
    else:
        cost_after = lmsr_cost(b, existing_yes, existing_no + shares)

    actual_cost = cost_after - cost_before
    shares_bought = shares * (trade.amount / max(actual_cost, 0.001))

    position = Position(
        id=str(uuid.uuid4()),
        user_id=trade.user_id,
        market_id=market_id,
        position=trade.position,
        shares=shares_bought,
        cost=trade.amount,
    )
    user.points -= trade.amount
    user.total_trades += 1
    market.total_volume += trade.amount

    # Update market prices
    new_yes = existing_yes + (shares_bought if trade.position == "yes" else 0)
    new_no = existing_no + (shares_bought if trade.position == "no" else 0)
    market.yes_price = lmsr_price(b, new_yes, new_no)
    market.no_price = 1.0 - market.yes_price

    db.add(position)
    db.commit()

    return {
        "shares_bought": round(shares_bought, 4),
        "price_paid": trade.amount,
        "new_yes_price": round(market.yes_price, 4),
        "new_no_price": round(market.no_price, 4),
    }


@router.post("/{market_id}/resolve")
def resolve_market(market_id: str, outcome: Literal["yes", "no"], db: Session = Depends(get_db)):
    market = db.query(Market).filter(Market.id == market_id).first()
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")

    market.status = MarketStatus.resolved_yes if outcome == "yes" else MarketStatus.resolved_no
    market.resolved_at = datetime.utcnow()

    # Pay out winners
    winning_positions = [p for p in market.positions if p.position == outcome]
    total_pool = market.total_volume
    total_winning_shares = sum(p.shares for p in winning_positions)

    for pos in winning_positions:
        payout = int(total_pool * (pos.shares / total_winning_shares)) if total_winning_shares > 0 else 0
        pos.payout = payout
        pos.user.points += payout

    db.commit()
    return {"status": f"resolved_{outcome}", "total_pool": total_pool, "winners": len(winning_positions)}
