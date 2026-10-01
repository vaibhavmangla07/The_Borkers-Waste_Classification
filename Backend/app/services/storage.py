import io
import uuid
from pathlib import Path
from fastapi import HTTPException, UploadFile, status
from PIL import Image

from app.core.config import settings
from app.core.logging import logger

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/bmp",
    "application/octet-stream"  # Some clients omit or generalize mime type
}


class StorageService:
    def __init__(self, upload_dir: Path = settings.upload_dir_path):
        self.upload_dir = upload_dir

    async def save_upload(self, file: UploadFile) -> tuple[str, str, int, str]:
        """
        Validate, inspect, and save an uploaded image file securely.
        Returns:
            (stored_filename, relative_url, file_size_bytes, image_format)
        """
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file must have a valid filename."
            )

        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file extension '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            )

        # Read content and enforce size limits
        content = await file.read()
        file_size = len(content)

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty."
            )

        if file_size > settings.max_upload_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB."
            )

        # Verify image validity with PIL
        try:
            with Image.open(io.BytesIO(content)) as img:
                img.verify()
                img_format = img.format or ext.lstrip(".").upper()
        except Exception as e:
            logger.warning(f"Corrupt or invalid image upload '{file.filename}': {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file is not a valid or readable image."
            )

        # Generate unique storage filename
        stored_filename = f"{uuid.uuid4().hex}{ext}"
        destination = self.upload_dir / stored_filename

        # Write to disk
        try:
            with open(destination, "wb") as f:
                f.write(content)
        except Exception as e:
            logger.error(f"Failed to save upload to {destination}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to persist uploaded image on server."
            )

        # Reset pointer for downstream readers if needed
        await file.seek(0)

        image_url = f"/static/uploads/{stored_filename}"
        return stored_filename, image_url, file_size, img_format


storage_service = StorageService()
