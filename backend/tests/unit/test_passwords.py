from app.auth.passwords import hash_password, verify_password


def test_hash_and_verify_roundtrip() -> None:
    hashed = hash_password("my-secret-password")
    assert verify_password("my-secret-password", hashed)


def test_wrong_password_returns_false() -> None:
    hashed = hash_password("correct")
    assert not verify_password("wrong", hashed)


def test_empty_password() -> None:
    hashed = hash_password("")
    assert verify_password("", hashed)
    assert not verify_password("notempty", hashed)


def test_verify_invalid_hash_returns_false() -> None:
    assert not verify_password("anything", "not-a-valid-hash")
