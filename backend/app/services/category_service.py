from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException

from app.models.waste_category import WasteCategory
from app.models.disposal_guideline import DisposalGuideline

class CategoryService:
    @staticmethod
    def get_categories(db: Session, skip: int = 0, limit: int = 100):
        stmt = select(WasteCategory).offset(skip).limit(limit)
        return db.scalars(stmt).all()

    @staticmethod
    def get_category_by_slug(db: Session, slug: str):
        stmt = select(WasteCategory).where(WasteCategory.slug == slug)
        category = db.scalars(stmt).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category

    @staticmethod
    def get_category_guidance(db: Session, slug: str):
        category = CategoryService.get_category_by_slug(db, slug)
        stmt = select(DisposalGuideline).where(DisposalGuideline.category_id == category.id)
        return db.scalars(stmt).all()
