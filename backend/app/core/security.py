from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

ALGORITHM = "HS256"
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    hashed_password = password_hash.hash(password)
    if not isinstance(hashed_password, str):
        raise TypeError("PasswordHash.hash() must return a string")
    return hashed_password


def verify_password(password: str, hashed_password: str) -> bool:
    is_valid = password_hash.verify(password, hashed_password)
    if not isinstance(is_valid, bool):
        raise TypeError("PasswordHash.verify() must return a boolean")
    return is_valid


def create_access_token(user_id: UUID, role: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": str(user_id), "role": role, "exp": expires_at},
        settings.secret_key.get_secret_value(),
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, object] | None:
    try:
        return jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[ALGORITHM],
        )
    except jwt.PyJWTError:
        return None


def token_subject(token: str) -> UUID | None:
    claims = decode_access_token(token)
    subject = claims.get("sub") if claims else None
    if not isinstance(subject, str) or not subject:
        return None
    try:
        return UUID(subject)
    except ValueError:
        return None
