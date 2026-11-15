from app.core.security import hash_password, verify_password


def test_password_hash_verifies_only_matching_password() -> None:
    hashed = hash_password("Correct-Horse-42!")

    assert hashed != "Correct-Horse-42!"
    assert verify_password("Correct-Horse-42!", hashed)
    assert not verify_password("incorrect", hashed)
