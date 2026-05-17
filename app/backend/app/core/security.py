from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import jwt

from app.backend.app.core.config import get_settings


def verify_password(password: str, password_hash: str) -> bool:
    """Return True if plaintext password matches the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except ValueError:
        return False


def hash_password(password: str) -> str:
    """Generate and return a bcrypt hash of the given plaintext password."""
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")


def create_access_token(user_id: int, role_name: str) -> str:
    """Create a signed JWT containing the user ID and role, expiring per settings."""
    settings = get_settings()
    expires_at = datetime.now(UTC) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "role": role_name,
        "exp": expires_at,
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT, returning its payload dict. Raises on invalid/expired tokens."""
    settings = get_settings()
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
