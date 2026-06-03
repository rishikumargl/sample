from fastapi import APIRouter
from backend.app.models import HealthResponse

router = APIRouter(tags=["health"])

@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        message="Enterprise Knowledge Assistant API is running"
    )
