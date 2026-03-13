"""
PostgreSQL connection management for the Casino auth system.

Reads DATABASE_URL from the environment (or a .env file in the project root).
If the connection fails, the app continues in offline (JSON) mode.
"""

from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

log = logging.getLogger(__name__)

_DEFAULT_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/casino_db"

_engine = None
_SessionLocal: Optional[object] = None
_db_available: bool = False


def _try_load_dotenv() -> None:
    """Load .env from the project root if python-dotenv is installed."""
    try:
        from dotenv import load_dotenv  # type: ignore[import-untyped]

        root_env = Path(__file__).parent.parent / ".env"
        if root_env.exists():
            load_dotenv(root_env, override=False)
    except ImportError:
        pass  # optional dependency


def get_database_url() -> str:
    return os.environ.get("DATABASE_URL", _DEFAULT_URL)


def init_db() -> bool:
    """
    Attempt to connect to PostgreSQL and initialise the session factory.
    Returns True on success, False if unavailable (offline mode).
    """
    global _engine, _SessionLocal, _db_available

    _try_load_dotenv()

    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker

        url = get_database_url()
        _engine = create_engine(url, pool_pre_ping=True, echo=False, future=True)

        # Verify the connection works before declaring success
        with _engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        _SessionLocal = sessionmaker(
            bind=_engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
        _db_available = True

        safe = url.split("@")[-1] if "@" in url else url
        log.info("PostgreSQL connected: %s", safe)
        return True

    except Exception as exc:
        log.warning("PostgreSQL unavailable (%s). Offline mode active.", exc)
        _db_available = False
        return False


def is_db_available() -> bool:
    """Return True if PostgreSQL was successfully initialised."""
    return _db_available


def create_tables() -> None:
    """Create all tables defined in models (idempotent – safe to call multiple times)."""
    from .models import Base

    if _engine is not None:
        Base.metadata.create_all(bind=_engine)
        log.info("Database tables created/verified.")


@contextmanager
def get_session() -> Generator:
    """Yield a SQLAlchemy Session with automatic commit/rollback."""
    if _SessionLocal is None:
        raise RuntimeError("Database not initialised. Call init_db() first.")

    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
