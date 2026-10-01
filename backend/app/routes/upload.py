from fastapi import APIRouter, UploadFile, File
from app.schemas.upload import UploadResponse
from app.services.upload_service import UploadService

router = APIRouter(prefix="/api/upload", tags=["upload"])

@router.post("", response_model=UploadResponse)
def upload_image(file: UploadFile = File(...)):
    """
    Upload an image for waste classification.
    """
    result = UploadService.process_upload(file)
    return UploadResponse(**result)
