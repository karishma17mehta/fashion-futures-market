from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal

router = APIRouter()


class Market(BaseModel):
    id: str
    trend_id: str
    question: str          # e.g. "Will sheer layering appear on 3+ major brand homepages by Sept 1?"
    resolution_date: str
    resolution_criteria: str
    yes_price: float       # 0.0 - 1.0, implied probability
    no_price: float
    total_volume: int      # total points traded
    status: Literal["open", "resolved_yes", "resolved_no", "voided"]


class TradeRequest(BaseModel):
    user_id: str
    market_id: str
    position: Literal["yes", "no"]
    amount: int            # points to spend


@router.get("/")
def list_markets(status: str = "open"):
    # TODO: fetch from DB
    return {"markets": [], "total": 0}


@router.get("/{market_id}")
def get_market(market_id: str):
    # TODO: fetch from DB
    raise HTTPException(status_code=404, detail="Market not found")


@router.post("/{market_id}/trade")
def place_trade(market_id: str, trade: TradeRequest):
    """Place a YES or NO position using LMSR pricing."""
    # TODO: LMSR market maker logic
    return {"status": "pending"}


@router.post("/{market_id}/resolve")
def resolve_market(market_id: str):
    """Trigger AI oracle to resolve a market."""
    # TODO: check Google Trends + brand scrapers
    return {"status": "resolution_queued"}
