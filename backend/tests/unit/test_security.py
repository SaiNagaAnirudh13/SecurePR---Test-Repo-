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


def test_access_token_contains_subject_and_role() -> None:
    user_id = uuid4()

    token = create_access_token(user_id, "admin")
    claims = decode_access_token(token)

    assert token_subject(token) == user_id
    assert claims is not None
    assert claims["role"] == "admin"


def test_invalid_and_expired_tokens_are_rejected() -> None:
    invalid_signature_token = jwt.encode(
        {
            "sub": str(uuid4()),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=1),
        },
        "incorrect-secret-that-is-at-least-32-bytes",
        algorithm=ALGORITHM,
    )
    expired_token = jwt.encode(
        {
            "sub": str(uuid4()),
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
        },
        settings.secret_key.get_secret_value(),
        algorithm=ALGORITHM,
    )

    assert decode_access_token("not-a-jwt") is None
    assert decode_access_token(invalid_signature_token) is None
    assert token_subject(expired_token) is None


def test_access_token_with_non_string_subject_is_rejected() -> None:
    token = jwt.encode(
        {"sub": 123},
        settings.secret_key.get_secret_value(),
        algorithm=ALGORITHM,
    )

    assert token_subject(token) is None
