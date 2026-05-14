from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_session
from app.models import Detection, User
from app.schemas import DetectionList, DetectionPublic

router = APIRouter(prefix="/api/v1/detections", tags=["detections"])


@router.get("", response_model=DetectionList)
async def list_detections(
    session: Annotated[AsyncSession, Depends(get_session)],
    _current_user: Annotated[User, Depends(get_current_user)],
) -> DetectionList:
    count_result = await session.execute(select(func.count()).select_from(Detection))
    total = count_result.scalar_one()

    items_result = await session.execute(
        select(Detection).order_by(Detection.updated_at.desc())
    )
    items = items_result.scalars().all()

    return DetectionList(
        items=[DetectionPublic.model_validate(d) for d in items],
        total=total,
    )
