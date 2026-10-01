from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.analytics import AnalyticsSummaryResponse, CategoryAnalyticsListResponse, RecentActivityListResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary(db: Session = Depends(get_db)):
    """
    Get summary statistics for all classifications.
    """
    return AnalyticsSummaryResponse(**AnalyticsService.get_summary(db))

@router.get("/categories", response_model=CategoryAnalyticsListResponse)
def get_category_distribution(db: Session = Depends(get_db)):
    """
    Get distribution of classifications across all active categories.
    """
    return CategoryAnalyticsListResponse(**AnalyticsService.get_category_distribution(db))

@router.get("/recent", response_model=RecentActivityListResponse)
def get_recent_activity(
    limit: int = Query(10, ge=1, le=50, description="Number of recent activities to return"),
    db: Session = Depends(get_db)
):
    """
    Get the most recent classifications.
    """
    return RecentActivityListResponse(**AnalyticsService.get_recent_activity(db, limit))
