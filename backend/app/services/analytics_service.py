from sqlalchemy.orm import Session
from sqlalchemy import select, func, case

from app.models.classification import Classification
from app.models.waste_category import WasteCategory
from app.ai.config import get_confidence_level

class AnalyticsService:
    @staticmethod
    def get_summary(db: Session):
        total_classifications = db.scalar(select(func.count(Classification.id))) or 0
        total_categories = db.scalar(select(func.count(WasteCategory.id)).where(WasteCategory.is_active == True)) or 0
        
        avg_conf = db.scalar(select(func.avg(Classification.confidence))) or 0.0
        
        # confidence buckets
        buckets = db.execute(
            select(
                func.sum(case(((Classification.confidence >= 0.80), 1), else_=0)).label("high"),
                func.sum(case(((Classification.confidence >= 0.60) & (Classification.confidence < 0.80), 1), else_=0)).label("medium"),
                func.sum(case(((Classification.confidence < 0.60), 1), else_=0)).label("low")
            )
        ).first()
        
        high_count = int(buckets.high) if buckets and buckets.high else 0
        medium_count = int(buckets.medium) if buckets and buckets.medium else 0
        low_count = int(buckets.low) if buckets and buckets.low else 0
        
        most_cat_info = None
        if total_classifications > 0:
            most_cat_row = db.execute(
                select(WasteCategory.id, WasteCategory.name, WasteCategory.slug, func.count(Classification.id).label("cnt"))
                .join(Classification, WasteCategory.id == Classification.predicted_category_id)
                .group_by(WasteCategory.id)
                .order_by(func.count(Classification.id).desc(), WasteCategory.name.asc())
                .limit(1)
            ).first()
            if most_cat_row:
                most_cat_info = {
                    "id": most_cat_row.id,
                    "name": most_cat_row.name,
                    "slug": most_cat_row.slug,
                    "count": most_cat_row.cnt
                }

        return {
            "total_classifications": total_classifications,
            "total_categories": total_categories,
            "most_classified_category": most_cat_info,
            "average_confidence": float(avg_conf),
            "high_confidence_count": high_count,
            "medium_confidence_count": medium_count,
            "low_confidence_count": low_count
        }

    @staticmethod
    def get_category_distribution(db: Session):
        total_classifications = db.scalar(select(func.count(Classification.id))) or 0
        
        rows = db.execute(
            select(
                WasteCategory.id, 
                WasteCategory.name, 
                WasteCategory.slug, 
                func.count(Classification.id).label("cnt")
            )
            .outerjoin(Classification, WasteCategory.id == Classification.predicted_category_id)
            .where(WasteCategory.is_active == True)
            .group_by(WasteCategory.id)
            .order_by(func.count(Classification.id).desc(), WasteCategory.name.asc())
        ).all()
        
        items = []
        for r in rows:
            percentage = 0.0
            if total_classifications > 0:
                percentage = round((r.cnt / float(total_classifications)) * 100, 2)
            items.append({
                "category_id": r.id,
                "category_name": r.name,
                "category_slug": r.slug,
                "classification_count": r.cnt,
                "percentage": percentage
            })
            
        return {
            "items": items,
            "total_classifications": total_classifications
        }

    @staticmethod
    def get_recent_activity(db: Session, limit: int = 10):
        stmt = select(Classification).order_by(Classification.created_at.desc(), Classification.id.desc()).limit(limit)
        classifications = db.scalars(stmt).all()
        items = []
        for c in classifications:
            items.append({
                "id": c.id,
                "image_filename": c.image_filename,
                "category": {
                    "id": c.predicted_category.id,
                    "name": c.predicted_category.name,
                    "slug": c.predicted_category.slug
                },
                "confidence": c.confidence,
                "confidence_level": get_confidence_level(c.confidence),
                "created_at": c.created_at
            })
        return {"items": items}
