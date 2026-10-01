from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import logger
from app.db.session import get_db
from app.models.classification import WasteScan
from app.schemas.classification import (
    CategoryBreakdownItem,
    ClassificationStatsResponse,
    WasteScanListResponse,
    WasteScanResponse,
)

router = APIRouter()


@router.get("", response_model=WasteScanListResponse, summary="Get Paginated Scan History")
async def get_history(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    category: Optional[str] = Query(None, description="Filter by category (organic, recyclable, etc.)"),
    recyclable: Optional[bool] = Query(None, description="Filter by recyclable status"),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieves historical classification records with filtering and pagination.
    """
    query = select(WasteScan)
    count_query = select(func.count(WasteScan.id))

    if category:
        query = query.where(WasteScan.category == category.lower())
        count_query = count_query.where(WasteScan.category == category.lower())
    if recyclable is not None:
        query = query.where(WasteScan.recyclable == recyclable)
        count_query = count_query.where(WasteScan.recyclable == recyclable)

    # Total count
    total_res = await db.execute(count_query)
    total = total_res.scalar() or 0

    # Paginated results
    offset = (page - 1) * page_size
    query = query.order_by(desc(WasteScan.created_at)).offset(offset).limit(page_size)
    items_res = await db.execute(query)
    items = items_res.scalars().all()

    return WasteScanListResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[WasteScanResponse.model_validate(item) for item in items]
    )


@router.get("/stats", response_model=ClassificationStatsResponse, summary="Get Classification Analytics & Stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    """
    Returns aggregated metrics across all waste scans.
    """
    # Total count
    total_q = await db.execute(select(func.count(WasteScan.id)))
    total_scans = total_q.scalar() or 0

    if total_scans == 0:
        return ClassificationStatsResponse(
            total_scans=0,
            recyclable_count=0,
            non_recyclable_count=0,
            recyclable_rate_pct=0.0,
            average_confidence=0.0,
            category_breakdown=[]
        )

    # Recyclable count
    rec_q = await db.execute(select(func.count(WasteScan.id)).where(WasteScan.recyclable == True))
    recyclable_count = rec_q.scalar() or 0
    non_recyclable_count = total_scans - recyclable_count
    recyclable_rate = round((recyclable_count / total_scans) * 100, 2)

    # Average confidence
    avg_conf_q = await db.execute(select(func.avg(WasteScan.confidence)))
    avg_conf = round(float(avg_conf_q.scalar() or 0.0), 3)

    # Category breakdown
    cat_breakdown_q = await db.execute(
        select(WasteScan.category, func.count(WasteScan.id))
        .group_by(WasteScan.category)
    )
    breakdown = []
    for cat, count in cat_breakdown_q.all():
        pct = round((count / total_scans) * 100, 2)
        breakdown.append(CategoryBreakdownItem(category=cat, count=count, percentage=pct))

    return ClassificationStatsResponse(
        total_scans=total_scans,
        recyclable_count=recyclable_count,
        non_recyclable_count=non_recyclable_count,
        recyclable_rate_pct=recyclable_rate,
        average_confidence=avg_conf,
        category_breakdown=breakdown
    )


@router.get("/{scan_id}", response_model=WasteScanResponse, summary="Get Scan Details by ID")
async def get_scan_by_id(scan_id: int, db: AsyncSession = Depends(get_db)):
    """
    Fetches full metadata and classification results for a single scan.
    """
    result = await db.execute(select(WasteScan).where(WasteScan.id == scan_id))
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan record with ID {scan_id} was not found."
        )
    return scan


@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete Scan Record")
async def delete_scan(scan_id: int, db: AsyncSession = Depends(get_db)):
    """
    Deletes the scan from database and removes stored image file from disk.
    """
    result = await db.execute(select(WasteScan).where(WasteScan.id == scan_id))
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan record with ID {scan_id} was not found."
        )

    # Remove file from disk if it exists
    file_path = settings.upload_dir_path / scan.stored_filename
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            logger.warning(f"Could not delete physical file {file_path}: {e}")

    await db.execute(delete(WasteScan).where(WasteScan.id == scan_id))
    await db.commit()
    logger.info(f"Deleted scan record {scan_id} and associated file.")
    return None
