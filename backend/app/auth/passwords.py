from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

_ph = PasswordHasher()

# Pre-computed dummy hash used to equalize timing when a user is not found.
_DUMMY_HASH = _ph.hash("dummy-timing-equalization-value")


def hash_password(plain: str) -> str:
    return _ph.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _ph.verify(hashed, plain)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def dummy_verify() -> None:
    """Call when no user is found to equalize timing with a failed password check."""
    verify_password("dummy", _DUMMY_HASH)
