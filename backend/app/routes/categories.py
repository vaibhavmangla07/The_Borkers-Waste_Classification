from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.category import CategoryResponse, CategoryDetailResponse, DisposalGuidelineResponse
from app.services.category_service import CategoryService

router = APIRouter(prefix="/api/categories", tags=["categories"])

@router.get("", response_model=list[CategoryResponse])
def get_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieve all waste categories."""
    return CategoryService.get_categories(db, skip=skip, limit=limit)

@router.get("/{slug}", response_model=CategoryDetailResponse)
def get_category(slug: str, db: Session = Depends(get_db)):
    """Retrieve a specific waste category by slug."""
    return CategoryService.get_category_by_slug(db, slug)

@router.get("/{slug}/guidance", response_model=list[DisposalGuidelineResponse])
def get_category_guidance(slug: str, db: Session = Depends(get_db)):
    """Retrieve disposal guidance for a specific waste category."""
    return CategoryService.get_category_guidance(db, slug)
