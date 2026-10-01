from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List

from app.schemas.category import CategoryResponse, DisposalGuidelineResponse
from app.schemas.prediction import PredictionResult

class ClassificationPredictionResponse(BaseModel):
    rank: int
    label: str
    confidence: float
    confidence_level: str

    model_config = ConfigDict(from_attributes=True)

class ClassificationResponse(BaseModel):
    id: int
    image_filename: str
    predicted_category: CategoryResponse
    confidence: float
    confidence_level: str
    model_name: str
    model_version: str
    predictions: List[ClassificationPredictionResponse]
    guidance: List[DisposalGuidelineResponse]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
