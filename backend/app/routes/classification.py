"""
classification.py — FastAPI routes for waste classification and history.

Routes:
  POST /api/classify              — classify an uploaded image
  GET  /api/history               — paginated history list
  GET  /api/history/{id}          — single classification detail
  GET  /api/history/{id}/image    — serve the original uploaded image
"""
from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.database.session import get_db
from app.schemas.classification import ClassificationResponse, HistoryListResponse
from app.services.classification_service import ClassificationService

router = APIRouter(tags=["classification"])


# ─── Classification ──────────────────────────────────────────────────────────

@router.post("/api/classify", response_model=ClassificationResponse)
def classify_image(
    image: UploadFile = File(..., description="Waste item image (JPEG / PNG / WEBP, ≤ 10 MB)"),
    db: Session = Depends(get_db),
):
    """
    Upload and classify a waste image.

    - **image**: multipart/form-data field named `image`
    - Returns a `ClassificationResponse` matching the frontend API contract.
    """
    return ClassificationService.classify(image, db)


# ─── History ─────────────────────────────────────────────────────────────────

@router.get("/api/history", response_model=HistoryListResponse)
def get_history(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category name (case-insensitive)"),
    db: Session = Depends(get_db),
):
    """Retrieve paginated classification history, newest first."""
    return ClassificationService.get_history(db, page=page, limit=limit, category=category)


@router.get("/api/history/{item_id}", response_model=ClassificationResponse)
def get_history_item(item_id: int, db: Session = Depends(get_db)):
    """Retrieve a single classification result by its ID."""
    return ClassificationService.get_history_item(item_id, db)


@router.get("/api/history/{item_id}/image")
def get_history_image(item_id: int, db: Session = Depends(get_db)):
    """Serve the original uploaded image for a classification record."""
    image_path = ClassificationService.get_image_path(item_id, db)
    return FileResponse(
        path=str(image_path),
        media_type="image/jpeg",  # browser handles actual type
        filename=image_path.name,
    )
