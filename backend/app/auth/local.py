from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.passwords import dummy_verify, verify_password
from app.auth.provider import AuthResult
from app.models import User


class LocalAuthProvider:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def authenticate(self, username: str, password: str) -> AuthResult | None:
        result = await self._session.execute(
            select(User).where(
                or_(User.username == username, User.email == username),
                User.is_active.is_(True),
            )
        )
        user = result.scalar_one_or_none()

        if user is None:
            # Equalize timing so callers can't distinguish "no such user" from
            # "wrong password" via response latency.
            dummy_verify()
            return None

        if not verify_password(password, user.password_hash):
            return None

        return AuthResult(user=user)

    async def get_user(self, user_id: UUID) -> User | None:
        return await self._session.get(User, user_id)
