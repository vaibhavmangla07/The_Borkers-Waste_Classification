from pydantic import BaseModel

class UploadResponse(BaseModel):
    filename: str
    original_filename: str
    content_type: str
    size_bytes: int
    width: int
    height: int
    message: str
