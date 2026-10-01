from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional


# ─── Sub-schemas for the frontend contract ────────────────────────────────────

class PredictionItem(BaseModel):
    """Single ranked prediction entry (frontend shape)."""
    category: str
    confidence: float
    confidence_level: str

    model_config = ConfigDict(from_attributes=True)


class DisposalResponse(BaseModel):
    """Disposal guidance object (frontend shape)."""
    title: str
    bin_type: str
    instructions: List[str]
    avoid: List[str]


# ─── Primary classification response (matches frontend API contract) ──────────

class ClassificationResponse(BaseModel):
    """
    Response shape emitted by POST /api/classify.

    Field mapping vs internal DB:
      classification_id  ← Classification.id
      category           ← WasteCategory.name
      predictions        ← list[ClassificationPrediction] (reshaped)
      disposal           ← DisposalGuideline (reshaped)
      inference_ms       ← computed timing
    """
    classification_id: int
    category: str
    confidence: float
    confidence_level: str
    message: str
    predictions: List[PredictionItem]
    disposal: Optional[DisposalResponse]
    inference_ms: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ─── History item response (GET /api/history/:id) ────────────────────────────

class HistoryItem(BaseModel):
    """Compact history list entry."""
    id: int
    category: str
    confidence: float
    confidence_level: str
    created_at: datetime
    thumbnail: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class HistoryListResponse(BaseModel):
    """Paginated history list."""
    items: List[HistoryItem]
    total: int
    page: int
    limit: int

