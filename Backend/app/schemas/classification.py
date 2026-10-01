from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class WasteCategory(str, Enum):
    ORGANIC = "organic"
    RECYCLABLE = "recyclable"
    HAZARDOUS = "hazardous"
    NON_RECYCLABLE = "non_recyclable"


class CategoryInfo(BaseModel):
    category: WasteCategory
    display_name: str
    bin_color: str
    bin_hex: str
    description: str
    common_items: List[str]
    disposal_rules: List[str]


class ClassificationResult(BaseModel):
    """Inference result returned by classifier engine."""
    category: WasteCategory
    item_name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    recyclable: bool
    bin_color: str
    disposal_guidance: str
    eco_tip: str
    alternatives: Optional[List[Dict[str, float]]] = None


class WasteScanResponse(BaseModel):
    """Full database representation of a waste scan."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_filename: str
    stored_filename: str
    image_url: str
    category: str
    item_name: str
    confidence: float
    recyclable: bool
    bin_color: str
    disposal_guidance: str
    eco_tip: str
    image_format: Optional[str] = None
    file_size_bytes: int
    processing_time_ms: float
    created_at: datetime


class WasteScanListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[WasteScanResponse]


class CategoryBreakdownItem(BaseModel):
    category: str
    count: int
    percentage: float


class ClassificationStatsResponse(BaseModel):
    total_scans: int
    recyclable_count: int
    non_recyclable_count: int
    recyclable_rate_pct: float
    average_confidence: float
    category_breakdown: List[CategoryBreakdownItem]


class BatchClassificationResponse(BaseModel):
    total_processed: int
    successful: int
    failed: int
    results: List[WasteScanResponse]
    errors: List[Dict[str, str]]
