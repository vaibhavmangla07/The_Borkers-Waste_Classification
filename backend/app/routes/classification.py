from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.classification import ClassificationResponse
from app.services.classification_service import ClassificationService

router = APIRouter(prefix="/api/classify", tags=["classification"])

@router.post("", response_model=ClassificationResponse)
def classify_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload and classify an image using the AI model.
    """
    result = ClassificationService.classify(file, db)
    return ClassificationResponse(**result)
