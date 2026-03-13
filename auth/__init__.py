"""
auth – Authentication package for RuleTragaperrasJuego.

Provides user registration, login, and PostgreSQL-backed profile storage.
Public API:
    AuthManager   – register / login logic
    init_db()     – connect to PostgreSQL (call once at startup)
    is_db_available() – True when PostgreSQL is reachable
    create_tables()   – idempotent table creation
"""

from .auth_manager import AuthManager
from .database import create_tables, init_db, is_db_available

__all__ = ["AuthManager", "init_db", "is_db_available", "create_tables"]
