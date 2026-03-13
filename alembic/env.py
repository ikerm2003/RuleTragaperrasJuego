"""
Alembic environment script.

Reads DATABASE_URL from the environment first; falls back to alembic.ini.
"""

from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# ── Alembic Config object ──────────────────────────────────────────────────
config = context.config

# Override sqlalchemy.url from environment variable if set
_db_url = os.environ.get("DATABASE_URL")
if _db_url:
    config.set_main_option("sqlalchemy.url", _db_url)

# Logging configuration from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import the metadata so Alembic can autogenerate migrations
from auth.models import Base  # noqa: E402

target_metadata = Base.metadata


# ── Migration helpers ──────────────────────────────────────────────────────

def run_migrations_offline() -> None:
    """Run migrations without a live DB connection (emits SQL to stdout)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live database connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
