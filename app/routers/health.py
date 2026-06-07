from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/health/ready")
async def readiness_check():
    return {"status": "ready"}

@router.get("/health/live")
async def liveness_check():
    return {"status": "alive"}
