from sqlalchemy import Column, String, Float, Integer, DateTime, Enum, ForeignKey, Text, Boolean
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime
import enum


class Base(DeclarativeBase):
    pass


class TrendStatus(str, enum.Enum):
    emerging   = "emerging"
    active     = "active"
    mainstream = "mainstream"
    dead       = "dead"


class MarketStatus(str, enum.Enum):
    open         = "open"
    resolved_yes = "resolved_yes"
    resolved_no  = "resolved_no"
    voided       = "voided"


class UserRank(str, enum.Enum):
    novice     = "novice"
    forecaster = "forecaster"
    oracle     = "oracle"
    legend     = "legend"


class Trend(Base):
    __tablename__ = "trends"

    id               = Column(String, primary_key=True)
    name             = Column(String, nullable=False)
    description      = Column(Text)
    ai_score         = Column(Float)
    ai_thesis        = Column(Text)
    source           = Column(String)
    signal_velocity  = Column(Float)
    status           = Column(Enum(TrendStatus), default=TrendStatus.emerging)
    created_at       = Column(DateTime, default=datetime.utcnow)
    # Cross-platform confirmation fields
    platform_count   = Column(Integer, default=1)   # how many platforms confirmed it
    confirmed_sources = Column(Text, default="")    # comma-separated sources
    # Score tracking
    score_updated_at = Column(DateTime, nullable=True)

    markets        = relationship("Market", back_populates="trend")
    score_history  = relationship("TrendScoreHistory", back_populates="trend")


class TrendScoreHistory(Base):
    """Weekly score snapshots so we can show score trends over time."""
    __tablename__ = "trend_score_history"

    id         = Column(String, primary_key=True)
    trend_id   = Column(String, ForeignKey("trends.id"))
    score      = Column(Float)
    velocity   = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    trend = relationship("Trend", back_populates="score_history")


class Market(Base):
    __tablename__ = "markets"

    id                   = Column(String, primary_key=True)
    trend_id             = Column(String, ForeignKey("trends.id"))
    question             = Column(Text, nullable=False)
    resolution_date      = Column(DateTime, nullable=False)
    resolution_criteria  = Column(Text, nullable=False)
    yes_price            = Column(Float, default=0.5)
    no_price             = Column(Float, default=0.5)
    liquidity_param      = Column(Float, default=100.0)
    total_volume         = Column(Integer, default=0)
    status               = Column(Enum(MarketStatus), default=MarketStatus.open)
    created_at           = Column(DateTime, default=datetime.utcnow)
    resolved_at          = Column(DateTime, nullable=True)
    # Auto-resolution tracking
    auto_resolve_checked = Column(DateTime, nullable=True)
    auto_resolve_signal  = Column(Text, nullable=True)   # what evidence triggered resolution

    trend     = relationship("Trend", back_populates="markets")
    positions = relationship("Position", back_populates="market")


class User(Base):
    __tablename__ = "users"

    id            = Column(String, primary_key=True)
    username      = Column(String, unique=True, nullable=False)
    email         = Column(String, nullable=True)          # for alerts
    points        = Column(Integer, default=1000)
    xp            = Column(Integer, default=0)             # experience points (gamification)
    streak_days   = Column(Integer, default=0)             # consecutive days active
    last_active   = Column(DateTime, nullable=True)        # for streak tracking
    rank          = Column(Enum(UserRank), default=UserRank.novice)
    accuracy_rate = Column(Float, default=0.0)
    total_trades  = Column(Integer, default=0)
    markets_won   = Column(Integer, default=0)
    markets_lost  = Column(Integer, default=0)
    created_at    = Column(DateTime, default=datetime.utcnow)

    positions = relationship("Position", back_populates="user")
    alerts    = relationship("TrendAlert", back_populates="user")
    activity  = relationship("UserActivity", back_populates="user")
    badges    = relationship("UserBadge", back_populates="user")


class Position(Base):
    __tablename__ = "positions"

    id         = Column(String, primary_key=True)
    user_id    = Column(String, ForeignKey("users.id"))
    market_id  = Column(String, ForeignKey("markets.id"))
    position   = Column(String)    # yes | no
    shares     = Column(Float)
    cost       = Column(Integer)
    payout     = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user   = relationship("User", back_populates="positions")
    market = relationship("Market", back_populates="positions")


class TrendAlert(Base):
    """User subscriptions: notify when a trend crosses a score threshold."""
    __tablename__ = "trend_alerts"

    id          = Column(String, primary_key=True)
    user_id     = Column(String, ForeignKey("users.id"))
    trend_name  = Column(String, nullable=False)   # wildcard match or exact
    min_score   = Column(Float, default=7.0)        # notify when score >= this
    source_filter = Column(String, nullable=True)   # optional: only tiktok, pinterest etc.
    active      = Column(Boolean, default=True)
    last_fired  = Column(DateTime, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="alerts")


# ── Gamification ──────────────────────────────────────────────────────────────

class UserActivity(Base):
    """Logs every point-earning action a user takes."""
    __tablename__ = "user_activity"

    id          = Column(String, primary_key=True)
    user_id     = Column(String, ForeignKey("users.id"))
    action      = Column(String, nullable=False)   # trade_placed, market_won, streak_bonus, badge_earned, early_adopter
    xp_earned   = Column(Integer, default=0)
    detail      = Column(Text, nullable=True)      # e.g. trend name, badge name
    created_at  = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="activity")


class UserBadge(Base):
    """Badges awarded to users."""
    __tablename__ = "user_badges"

    id          = Column(String, primary_key=True)
    user_id     = Column(String, ForeignKey("users.id"))
    badge_slug  = Column(String, nullable=False)   # trend_hunter, oracle, early_adopter, hot_streak etc.
    badge_name  = Column(String, nullable=False)
    badge_desc  = Column(Text, nullable=True)
    earned_at   = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="badges")
