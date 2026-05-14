"""Seed the database with development data.

Run with:  python -m app.seed
Or via:    make seed

SEEDED CREDENTIALS ARE FOR LOCAL DEVELOPMENT ONLY.
The seed password is publicly documented and must never be used in any
deployed environment.
"""

import asyncio
import os

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.passwords import hash_password
from app.database import AsyncSessionLocal
from app.models import Detection, DetectionStatus, Severity, User

log = structlog.get_logger()

_SEED_ADMIN_PASSWORD = os.getenv("FOUNDRY_SEED_ADMIN_PASSWORD", "foundry-dev-admin")

_SEED_DETECTIONS = [
    {
        "name": "Multiple Failed Login Attempts",
        "description": (
            "Detects brute-force or credential stuffing attacks by identifying "
            "a high volume of failed authentication events from a single source."
        ),
        "severity": Severity.high,
        "status": DetectionStatus.active,
        "query": "event.action:login_failure | stats count by src_ip | where count > 10",
    },
    {
        "name": "Suspicious PowerShell Execution",
        "description": (
            "Flags PowerShell invocations with commonly abused flags such as "
            "-EncodedCommand, -WindowStyle Hidden, or -NonInteractive."
        ),
        "severity": Severity.medium,
        "status": DetectionStatus.active,
        "query": (
            'process.name:powershell.exe AND process.args:("-EncodedCommand" OR '
            '"-WindowStyle Hidden" OR "-NonInteractive")'
        ),
    },
    {
        "name": "Outbound Connection to Known C2 Port",
        "description": (
            "Identifies outbound TCP connections to ports commonly used by "
            "command-and-control frameworks (4444, 8888, 1337)."
        ),
        "severity": Severity.critical,
        "status": DetectionStatus.draft,
        "query": "network.direction:outbound AND destination.port:(4444 OR 8888 OR 1337)",
    },
]


async def seed(session: AsyncSession) -> None:
    # Upsert admin user
    result = await session.execute(select(User).where(User.username == "admin"))
    admin = result.scalar_one_or_none()

    if admin is None:
        admin = User(
            username="admin",
            email="admin@foundry.local",
            password_hash=hash_password(_SEED_ADMIN_PASSWORD),
            is_active=True,
        )
        session.add(admin)
        await session.flush()
        log.info("seed_user_created", username="admin")
    else:
        log.info("seed_user_exists", username="admin")

    # Upsert detections
    for data in _SEED_DETECTIONS:
        existing = await session.execute(
            select(Detection).where(Detection.name == data["name"])
        )
        if existing.scalar_one_or_none() is None:
            detection = Detection(**data, author_id=admin.id)  # type: ignore[arg-type]
            session.add(detection)
            log.info("seed_detection_created", name=data["name"])
        else:
            log.info("seed_detection_exists", name=data["name"])

    await session.commit()
    log.info("seed_complete")


async def main() -> None:
    from app.logging import configure_logging
    configure_logging()
    async with AsyncSessionLocal() as session:
        await seed(session)


if __name__ == "__main__":
    asyncio.run(main())
