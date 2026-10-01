import os
import uuid
import logging
from pathlib import Path
from fastapi import UploadFile, HTTPException
from PIL import Image, UnidentifiedImageError

# Configure logger
logger = logging.getLogger(__name__)

from app.config import settings

# Constants
MAX_FILE_SIZE = settings.MAX_UPLOAD_MB * 1024 * 1024
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
UPLOAD_DIR = Path("storage/uploads")

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class UploadService:
    @staticmethod
    def process_upload(file: UploadFile) -> dict:
        """
        Validate, inspect, and save an uploaded image file.
        """
        if not file.filename:
            raise HTTPException(status_code=400, detail="Invalid or corrupted image file")

        # Check content type
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(status_code=400, detail="Invalid or corrupted image file")

        # Read file content for size and validation
        try:
            content = file.file.read()
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid or corrupted image file")

        if not content:
            raise HTTPException(status_code=400, detail="Invalid or corrupted image file")

        size_bytes = len(content)
        if size_bytes > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File too large")

        # Create a temporary file to validate with Pillow without leaving it open
        temp_path = UPLOAD_DIR / f"temp_{uuid.uuid4().hex}"
        try:
            with open(temp_path, "wb") as f:
                f.write(content)
        except Exception as e:
            logger.error(f"Failed to write temp file: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

        width, height = 0, 0
        extension = ""

        try:
            # Validate with Pillow
            with Image.open(temp_path) as img:
                img.verify()
                width, height = img.width, img.height
                fmt = img.format.lower() if img.format else ""

                if fmt not in ("jpeg", "png", "webp"):
                    raise HTTPException(status_code=400, detail="Invalid or corrupted image file")
                
                if fmt == "jpeg":
                    extension = ".jpg"
                elif fmt == "png":
                    extension = ".png"
                elif fmt == "webp":
                    extension = ".webp"
        except (UnidentifiedImageError, IOError, SyntaxError):
            temp_path.unlink(missing_ok=True)
            raise HTTPException(status_code=400, detail="Invalid or corrupted image file")
        except HTTPException:
            temp_path.unlink(missing_ok=True)
            raise
        except Exception as e:
            temp_path.unlink(missing_ok=True)
            logger.error(f"Image validation error: {e}")
            raise HTTPException(status_code=400, detail="Invalid or corrupted image file")

        # Generate final UUID filename
        new_filename = f"{uuid.uuid4()}{extension}"
        final_path = UPLOAD_DIR / new_filename

        # Move temp to final
        try:
            temp_path.rename(final_path)
        except Exception as e:
            temp_path.unlink(missing_ok=True)
            logger.error(f"Failed to move file to final path: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

        return {
            "filename": new_filename,
            "original_filename": Path(file.filename).name,
            "content_type": file.content_type,
            "size_bytes": size_bytes,
            "width": width,
            "height": height,
            "message": "Image uploaded successfully"
        }
