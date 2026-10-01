import math
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.classification import Classification
from app.models.waste_category import WasteCategory
from app.ai.config import get_confidence_level

class HistoryService:
    @staticmethod
    def get_classification_history(db: Session, page: int, page_size: int, category_slug: str | None = None):
        if page < 1 or page_size < 1:
            raise HTTPException(status_code=400, detail="Page and page_size must be >= 1")
        if page_size > 100:
            raise HTTPException(status_code=400, detail="Maximum page_size is 100")

        # Base query for counting
        count_stmt = select(func.count(Classification.id))
        
        # Base query for fetching
        stmt = select(Classification)

        if category_slug:
            # We need to filter by category slug
            cat_stmt = select(WasteCategory.id).where(WasteCategory.slug == category_slug)
            category_id = db.scalar(cat_stmt)
            if not category_id:
                raise HTTPException(status_code=404, detail=f"Category '{category_slug}' not found")
            
            count_stmt = count_stmt.where(Classification.predicted_category_id == category_id)
            stmt = stmt.where(Classification.predicted_category_id == category_id)

        # Get total count
        total = db.scalar(count_stmt) or 0
        total_pages = math.ceil(total / page_size) if total > 0 else 0

        # Apply ordering and pagination
        stmt = stmt.order_by(Classification.created_at.desc(), Classification.id.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        classifications = db.scalars(stmt).all()
        
        items = []
        for c in classifications:
            # Format predictions
            predictions = []
            for p in c.predictions:
                predictions.append({
                    "rank": p.rank,
                    "label": p.category.slug,
                    "confidence": p.confidence,
                    "confidence_level": get_confidence_level(p.confidence)
                })
                
            items.append({
                "id": c.id,
                "image_filename": c.image_filename,
                "predicted_category": c.predicted_category,
                "confidence": c.confidence,
                "confidence_level": get_confidence_level(c.confidence),
                "model_name": c.model_name,
                "model_version": c.model_version,
                "predictions": predictions,
                "created_at": c.created_at
            })

        return {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages
        }

    @staticmethod
    def get_classification_by_id(db: Session, classification_id: int):
        stmt = select(Classification).where(Classification.id == classification_id)
        c = db.scalar(stmt)
        if not c:
            raise HTTPException(status_code=404, detail=f"Classification {classification_id} not found")
            
        predictions = []
        for p in c.predictions:
            predictions.append({
                "rank": p.rank,
                "label": p.category.slug,
                "confidence": p.confidence,
                "confidence_level": get_confidence_level(p.confidence)
            })
            
        return {
            "id": c.id,
            "image_filename": c.image_filename,
            "predicted_category": c.predicted_category,
            "confidence": c.confidence,
            "confidence_level": get_confidence_level(c.confidence),
            "model_name": c.model_name,
            "model_version": c.model_version,
            "predictions": predictions,
            "created_at": c.created_at
        }
