import time
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app import __version__
from app.core.config import settings
from app.db.session import get_db
from app.schemas.health import HealthResponse
from app.services.classifier import classifier_service

router = APIRouter()
START_TIME = time.time()


@router.get("/health", response_model=HealthResponse, summary="Service Health & Diagnostics")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Checks backend health, database connectivity, and ML model status.
    """
    db_connected = False
    try:
        await db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False

    uptime_seconds = int(time.time() - START_TIME)

    return HealthResponse(
        status="healthy" if db_connected else "degraded",
        app_name=settings.PROJECT_NAME,
        version=__version__,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc),
        model_loaded=classifier_service.is_custom_model_loaded,
        model_path=settings.MODEL_PATH,
        db_connected=db_connected,
        details={
            "uptime_seconds": str(uptime_seconds),
            "upload_dir": str(settings.upload_dir_path),
            "max_upload_size_mb": str(settings.MAX_UPLOAD_SIZE_MB)
        }
    )
