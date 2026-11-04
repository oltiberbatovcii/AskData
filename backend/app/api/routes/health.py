"""Health check: lets you (and Docker later) see that the API is up."""

from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> HealthResponse:
    """Return a fixed 'ok' if the server is running."""
    return HealthResponse(status="ok")
