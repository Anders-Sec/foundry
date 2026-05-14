from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from app.models import User


@dataclass
class AuthResult:
    user: User


class AuthProvider(Protocol):
    async def authenticate(self, username: str, password: str) -> AuthResult | None: ...
    async def get_user(self, user_id: UUID) -> User | None: ...
