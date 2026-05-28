from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class User(BaseModel):
    id: str
    username: str
    points: int            # virtual currency balance
    rank: str              # novice | forecaster | oracle | legend
    accuracy_rate: float   # % of resolved markets called correctly
    total_trades: int


@router.get("/{user_id}")
def get_user(user_id: str):
    # TODO: fetch from DB
    return {}


@router.get("/{user_id}/positions")
def get_positions(user_id: str):
    """All open and closed market positions for a user."""
    # TODO: fetch from DB
    return {"positions": []}


@router.get("/leaderboard")
def leaderboard(limit: int = 50):
    """Top forecasters ranked by accuracy."""
    # TODO: fetch from DB
    return {"users": []}
