from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid

from db.session import get_db
from db.models import User, Position

router = APIRouter()


class UserCreate(BaseModel):
    username: str


class UserOut(BaseModel):
    id: str
    username: str
    points: int
    rank: str
    accuracy_rate: float
    total_trades: int

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
    users = db.query(User).order_by(User.accuracy_rate.desc(), User.total_trades.desc()).limit(limit).all()
    return {"users": [UserOut.from_orm(u) for u in users]}


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut.from_orm(user)


@router.get("/{user_id}/positions")
def get_positions(user_id: str, db: Session = Depends(get_db)):
    positions = db.query(Position).filter(Position.user_id == user_id).all()
    return {"positions": [PositionOut.from_orm(p) for p in positions]}
