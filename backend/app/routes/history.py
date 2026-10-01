from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.history import HistoryListResponse, HistoryItemResponse
from app.services.history_service import HistoryService

router = APIRouter(prefix="/api/history", tags=["history"])

@router.get("", response_model=HistoryListResponse)
def get_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    category: str | None = Query(None, description="Filter by category slug"),
    db: Session = Depends(get_db)
):
    """
    Get classification history with pagination and optional category filter.
    """
    result = HistoryService.get_classification_history(db, page, page_size, category)
    return HistoryListResponse(**result)

@router.get("/{classification_id}", response_model=HistoryItemResponse)
def get_history_detail(
    classification_id: int,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific classification by ID.
    """
    result = HistoryService.get_classification_by_id(db, classification_id)
    return HistoryItemResponse(**result)
