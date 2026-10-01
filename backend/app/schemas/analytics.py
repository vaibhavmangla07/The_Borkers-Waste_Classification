from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class CategorySimpleResponse(BaseModel):
    id: int
    name: str
    slug: str
    count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class AnalyticsSummaryResponse(BaseModel):
    total_classifications: int
    total_categories: int
    most_classified_category: Optional[CategorySimpleResponse]
    average_confidence: float
    high_confidence_count: int
    medium_confidence_count: int
    low_confidence_count: int

class CategoryAnalyticsResponse(BaseModel):
    category_id: int
    category_name: str
    category_slug: str
    classification_count: int
    percentage: float

class CategoryAnalyticsListResponse(BaseModel):
    items: List[CategoryAnalyticsResponse]
    total_classifications: int

class RecentActivityCategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    
    model_config = ConfigDict(from_attributes=True)

class RecentActivityResponse(BaseModel):
    id: int
    image_filename: str
    category: RecentActivityCategoryResponse
    confidence: float
    confidence_level: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class RecentActivityListResponse(BaseModel):
    items: List[RecentActivityResponse]
