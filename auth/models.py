"""
SQLAlchemy ORM models for the Casino authentication system.

Tables
------
users          – one row per registered player
user_profiles  – one-to-one extension with stats, balance, achievements and settings
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    # Allow legacy-style type annotations (e.g. on relationship fields)
    # alongside Column() declarations in SQLAlchemy 2.x.
    __allow_unmapped__ = True


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    profile: "UserProfile" = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r}>"


class UserProfile(Base):
    """Stores per-player game data: balance, stats, achievements and settings."""

    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # ── Balances ───────────────────────────────────────────────────────────
    current_balance = Column(Integer, default=1000, nullable=False)
    practice_balance = Column(Integer, default=10000, nullable=False)
    last_login_date = Column(String(10), nullable=True)  # YYYY-MM-DD

    # ── Statistics ─────────────────────────────────────────────────────────
    total_hands_played = Column(Integer, default=0, nullable=False)
    total_wins = Column(Integer, default=0, nullable=False)
    total_losses = Column(Integer, default=0, nullable=False)
    biggest_win = Column(Integer, default=0, nullable=False)
    total_wagered = Column(Integer, default=0, nullable=False)
    total_won = Column(Integer, default=0, nullable=False)
    poker_hands = Column(Integer, default=0, nullable=False)
    blackjack_hands = Column(Integer, default=0, nullable=False)
    roulette_spins = Column(Integer, default=0, nullable=False)
    slots_spins = Column(Integer, default=0, nullable=False)

    # ── Achievements (JSONB for indexability in PostgreSQL) ────────────────
    achievements_unlocked = Column(JSONB, default=list, nullable=False)
    achievements_progress = Column(JSONB, default=dict, nullable=False)

    # ── Daily missions ─────────────────────────────────────────────────────
    daily_missions = Column(JSONB, default=list, nullable=False)
    last_mission_date = Column(String(10), nullable=True)
    completed_today = Column(JSONB, default=list, nullable=False)

    # ── Display / interface / gameplay settings ────────────────────────────
    settings = Column(JSONB, default=dict, nullable=False)

    user: "User" = relationship("User", back_populates="profile")

    def __repr__(self) -> str:
        return f"<UserProfile user_id={self.user_id} balance={self.current_balance}>"
