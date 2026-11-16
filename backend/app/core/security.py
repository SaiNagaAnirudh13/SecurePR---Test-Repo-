from datetime import datetime, timedelta, timezone
from typing import Any, cast
from uuid import UUID

import jwt
from jwt import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import settings

ALGORITHM = "HS256"
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return cast(str, password_hash.hash(password))


def verify_password(password: str, hashed_password: str) -> bool:
    return cast(bool, password_hash.verify(password, hashed_password))


def create_access_token(user_id: UUID, role: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": str(user_id), "role": role, "exp": expires_at},
        settings.secret_key.get_secret_value(),
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[ALGORITHM],
        )
    except InvalidTokenError:
        return None


def token_subject(token: str) -> UUID | None:
    claims = decode_access_token(token)
    subject = claims.get("sub") if claims else None
    if not isinstance(subject, str):
        return None
    try:
        return UUID(subject)
    except ValueError:
        return None
