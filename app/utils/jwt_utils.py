from datetime import datetime, timedelta

import jwt

from app.config import settings


def create_access_token(user_id: int, is_admin: bool) -> str:
    now = datetime.utcnow()
    payload = {
        "sub": str(user_id),
        "is_admin": is_admin,
        "iat": now,
        "exp": now + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
    )
