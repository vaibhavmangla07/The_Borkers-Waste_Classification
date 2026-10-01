from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List

from app.schemas.category import CategoryResponse

class HistoryPredictionResponse(BaseModel):
    rank: int
    label: str
    confidence: float
    confidence_level: str

    model_config = ConfigDict(from_attributes=True)

class HistoryItemResponse(BaseModel):
    id: int
    image_filename: str
    predicted_category: CategoryResponse
    confidence: float
    confidence_level: str
    model_name: str
    model_version: str
    predictions: List[HistoryPredictionResponse]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class HistoryListResponse(BaseModel):
    items: List[HistoryItemResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
