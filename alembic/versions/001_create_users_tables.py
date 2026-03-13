"""Create users and user_profiles tables.

Revision ID: 001
Revises:
Create Date: 2026-03-13
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── users ──────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(50), unique=True, nullable=False),
        sa.Column("email", sa.String(200), unique=True, nullable=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("last_login", sa.DateTime(), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )
    op.create_index("ix_users_username", "users", ["username"])

    # ── user_profiles ──────────────────────────────────────────────────────
    op.create_table(
        "user_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            unique=True,
            nullable=False,
        ),
        # Balances
        sa.Column(
            "current_balance",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1000"),
        ),
        sa.Column(
            "practice_balance",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("10000"),
        ),
        sa.Column("last_login_date", sa.String(10), nullable=True),
        # Statistics
        sa.Column(
            "total_hands_played",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "total_wins", sa.Integer(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column(
            "total_losses", sa.Integer(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column(
            "biggest_win", sa.Integer(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column(
            "total_wagered", sa.Integer(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column(
            "total_won", sa.Integer(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column(
            "poker_hands", sa.Integer(), nullable=False, server_default=sa.text("0")
        ),
        sa.Column(
            "blackjack_hands",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "roulette_spins",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "slots_spins", sa.Integer(), nullable=False, server_default=sa.text("0")
        ),
        # JSONB columns (PostgreSQL native)
        sa.Column(
            "achievements_unlocked",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "achievements_progress",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "daily_missions",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("last_mission_date", sa.String(10), nullable=True),
        sa.Column(
            "completed_today",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "settings",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.create_index("ix_user_profiles_user_id", "user_profiles", ["user_id"])


def downgrade() -> None:
    op.drop_table("user_profiles")
    op.drop_table("users")
