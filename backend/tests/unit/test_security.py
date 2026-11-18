from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

from app.core.config import settings
from app.core.security import (
    ALGORITHM,
    create_access_token,
    decode_access_token,
    hash_password,
    token_subject,
    verify_password,
)


def test_password_hash_verifies_only_matching_password() -> None:
    hashed = hash_password("Correct-Horse-42!")

    assert hashed != "Correct-Horse-42!"
    assert verify_password("Correct-Horse-42!", hashed)
    assert not verify_password("incorrect", hashed)


def test_access_token_preserves_subject_role_and_expiration() -> None:
    user_id = uuid4()

    token = create_access_token(user_id, "admin")
    claims = decode_access_token(token)

    assert claims is not None
    assert claims["sub"] == str(user_id)
    assert claims["role"] == "admin"
    assert isinstance(claims["exp"], int)
    assert token_subject(token) == user_id


def test_access_token_rejects_invalid_signature() -> None:
    token = jwt.encode(
        {"sub": str(uuid4()), "role": "admin"},
        "incorrect-secret-for-token-test-32-bytes",
        algorithm=ALGORITHM,
    )

    assert decode_access_token(token) is None


def test_access_token_rejects_expired_token() -> None:
    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "role": "admin",
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
        },
        settings.secret_key.get_secret_value(),
        algorithm=ALGORITHM,
    )

    assert decode_access_token(token) is None


def test_access_token_rejects_malformed_token() -> None:
    assert decode_access_token("not-a-jwt") is None
