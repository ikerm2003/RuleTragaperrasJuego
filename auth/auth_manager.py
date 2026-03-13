"""
Authentication manager: user registration and login.

Password hashing uses PBKDF2-HMAC-SHA256 with 600 000 iterations.
No third-party crypto library required – only Python's standard hashlib.
"""

from __future__ import annotations

import hashlib
import logging
import re
import secrets
from datetime import datetime
from typing import Optional, Tuple

log = logging.getLogger(__name__)

# Only safe characters allowed in usernames
_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_.\-]{3,50}$")

_STAT_FIELDS = (
    "total_hands_played",
    "total_wins",
    "total_losses",
    "biggest_win",
    "total_wagered",
    "total_won",
    "poker_hands",
    "blackjack_hands",
    "roulette_spins",
    "slots_spins",
)


# ── Password helpers ──────────────────────────────────────────────────────────


def _hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Return (stored_hash, salt). The stored_hash encodes all parameters."""
    if salt is None:
        salt = secrets.token_hex(32)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations=600_000,
    )
    stored = f"pbkdf2$sha256$600000${salt}${key.hex()}"
    return stored, salt


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify *password* against a previously stored hash. Timing-safe."""
    try:
        parts = stored_hash.split("$")
        if len(parts) != 5 or parts[0] != "pbkdf2":
            return False
        _, alg, iters, salt, expected_hex = parts
        key = hashlib.pbkdf2_hmac(
            alg,
            password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations=int(iters),
        )
        return secrets.compare_digest(key.hex(), expected_hex)
    except Exception as exc:
        log.error("Password verification error: %s", exc)
        return False


# ── AuthManager ───────────────────────────────────────────────────────────────


class AuthManager:
    """Handles user registration and login backed by PostgreSQL."""

    # ── Registration ──────────────────────────────────────────────────────

    def register(
        self,
        username: str,
        password: str,
        email: str = "",
        confirm: str = "",
    ) -> Tuple[bool, str]:
        """
        Register a new user.

        Returns (True, success_msg) or (False, error_msg).
        All inputs are treated as untrusted.
        """
        from .database import get_session, is_db_available
        from .models import User, UserProfile

        # ── Input validation ──────────────────────────────────────────────
        username = username.strip()
        if not _USERNAME_RE.match(username):
            return (
                False,
                "El usuario debe tener entre 3 y 50 caracteres y solo puede "
                "contener letras, números, '_', '.' y '-'.",
            )
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres."
        if confirm and password != confirm:
            return False, "Las contraseñas no coinciden."
        if email and len(email) > 200:
            return False, "El correo electrónico es demasiado largo."

        if not is_db_available():
            return False, "Base de datos no disponible. Usa el modo offline."

        try:
            with get_session() as session:
                if session.query(User).filter(User.username == username).first():
                    return False, "El nombre de usuario ya está en uso."

                if email:
                    if session.query(User).filter(User.email == email).first():
                        return False, "El correo electrónico ya está registrado."

                password_hash, _ = _hash_password(password)
                user = User(
                    username=username,
                    email=email or None,
                    password_hash=password_hash,
                    created_at=datetime.utcnow(),
                    is_active=True,
                )
                session.add(user)
                session.flush()  # populate user.id
                session.add(UserProfile(user_id=user.id))

            return True, f"¡Bienvenido, {username}! Cuenta creada exitosamente."

        except Exception as exc:
            log.error("Registration error: %s", exc)
            return False, "Error al crear la cuenta. Inténtalo de nuevo."

    # ── Login ─────────────────────────────────────────────────────────────

    def login(
        self, username: str, password: str
    ) -> Tuple[Optional[dict], str]:
        """
        Authenticate a user.

        Returns ({'id': int, 'username': str}, success_msg)
        or (None, error_msg) on failure.
        """
        from .database import get_session, is_db_available
        from .models import User, UserProfile

        if not is_db_available():
            return None, "Base de datos no disponible. Usa el modo offline."

        try:
            with get_session() as session:
                user: Optional[User] = (
                    session.query(User).filter(User.username == username).first()
                )

                # Deliberately vague error to prevent user enumeration
                if not user or not user.is_active:
                    return None, "Usuario o contraseña incorrectos."

                if not verify_password(password, user.password_hash):
                    return None, "Usuario o contraseña incorrectos."

                user.last_login = datetime.utcnow()

                # Ensure profile exists (safeguard against incomplete registrations)
                if user.profile is None:
                    session.add(UserProfile(user_id=user.id))

                user_data = {"id": user.id, "username": user.username}

            return user_data, f"¡Bienvenido de vuelta, {username}!"

        except Exception as exc:
            log.error("Login error: %s", exc)
            return None, "Error al iniciar sesión. Inténtalo de nuevo."
