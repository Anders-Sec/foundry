from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE
from typing import Annotated
from fastapi import Depends

from app.database import get_session

router = APIRouter(tags=["health"])


@router.get("/healthz", include_in_schema=False)
async def liveness() -> JSONResponse:
    return JSONResponse(status_code=HTTP_200_OK, content={"status": "ok"})


@router.get("/readyz", include_in_schema=False)
async def readiness(session: Annotated[AsyncSession, Depends(get_session)]) -> JSONResponse:
    try:
        await session.execute(text("SELECT 1"))
        return JSONResponse(status_code=HTTP_200_OK, content={"status": "ok"})
    except Exception:
        return JSONResponse(
            status_code=HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unavailable"},
        )
