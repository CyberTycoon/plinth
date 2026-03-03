"""Health check endpoints."""

from fastapi import APIRouter, status
from pydantic import BaseModel
from datetime import datetime, timezone

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    timestamp: str
    version: str


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check if the API is running and healthy.",
)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="0.1.0",
    )


@router.get(
    "/ready",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Check if the API is ready to accept requests.",
)
async def readiness_check() -> HealthResponse:
    """Readiness check endpoint."""
    return HealthResponse(
        status="ready",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="0.1.0",
    )

