from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest
from pydantic import SecretStr

from app.core.config import settings
from app.core.security import (
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


def test_access_token_preserves_hs256_claims_and_subject() -> None:
    user_id = uuid4()

    token = create_access_token(user_id, "admin")
    claims = decode_access_token(token)

    assert claims is not None
    assert claims["sub"] == str(user_id)
    assert claims["role"] == "admin"
    assert claims["exp"] > datetime.now(timezone.utc).timestamp()
    assert token_subject(token) == user_id
    assert jwt.get_unverified_header(token)["alg"] == "HS256"


def test_access_token_rejects_expired_and_malformed_tokens() -> None:
    expired_token = jwt.encode(
        {"exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.secret_key.get_secret_value(),
        algorithm="HS256",
    )

    assert decode_access_token(expired_token) is None
    assert decode_access_token("not-a-jwt") is None


def test_access_token_rejects_invalid_signature() -> None:
    token = jwt.encode(
        {"sub": str(uuid4()), "role": "admin"},
        f"{settings.secret_key.get_secret_value()}-wrong",
        algorithm="HS256",
    )

    assert decode_access_token(token) is None


def test_access_token_rejects_unsupported_algorithm(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret = "s" * 48
    monkeypatch.setattr(settings, "secret_key", SecretStr(secret))
    token = jwt.encode(
        {"sub": str(uuid4()), "role": "admin"},
        secret,
        algorithm="HS384",
    )

    assert decode_access_token(token) is None
