from sqlalchemy import Column, String, Float, Integer, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
import enum


class Base(DeclarativeBase):
    pass


class TrendStatus(str, enum.Enum):
    emerging = "emerging"
    active = "active"
    mainstream = "mainstream"
    dead = "dead"


class MarketStatus(str, enum.Enum):
    open = "open"
    resolved_yes = "resolved_yes"
    resolved_no = "resolved_no"
    voided = "voided"


class UserRank(str, enum.Enum):
    novice = "novice"
    forecaster = "forecaster"
    oracle = "oracle"
    legend = "legend"


class Trend(Base):
    __tablename__ = "trends"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    ai_score = Column(Float)
    ai_thesis = Column(Text)
    source = Column(String)              # depop | reddit | tiktok | pinterest
    signal_velocity = Column(Float)      # % growth over 14 days
    status = Column(Enum(TrendStatus), default=TrendStatus.emerging)
    created_at = Column(DateTime, default=datetime.utcnow)

    markets = relationship("Market", back_populates="trend")


class Market(Base):
    __tablename__ = "markets"

    id = Column(String, primary_key=True)
    trend_id = Column(String, ForeignKey("trends.id"))
    question = Column(Text, nullable=False)
    resolution_date = Column(DateTime, nullable=False)
    resolution_criteria = Column(Text, nullable=False)
    yes_price = Column(Float, default=0.5)   # LMSR implied probability
    no_price = Column(Float, default=0.5)
    liquidity_param = Column(Float, default=100.0)  # LMSR b parameter
    total_volume = Column(Integer, default=0)
    status = Column(Enum(MarketStatus), default=MarketStatus.open)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    trend = relationship("Trend", back_populates="markets")
    positions = relationship("Position", back_populates="market")


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    points = Column(Integer, default=1000)   # starting balance
    rank = Column(Enum(UserRank), default=UserRank.novice)
    accuracy_rate = Column(Float, default=0.0)
    total_trades = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    positions = relationship("Position", back_populates="user")


class Position(Base):
    __tablename__ = "positions"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    market_id = Column(String, ForeignKey("markets.id"))
    position = Column(String)        # yes | no
    shares = Column(Float)           # LMSR shares purchased
    cost = Column(Integer)           # points spent
    payout = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="positions")
    market = relationship("Market", back_populates="positions")
