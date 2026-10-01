from pydantic import BaseModel
from typing import List

class PredictionResult(BaseModel):
    rank: int
    label: str
    confidence: float
    confidence_level: str

class PredictionResponse(BaseModel):
    predictions: List[PredictionResult]
    model_name: str
    model_version: str
    device: str
