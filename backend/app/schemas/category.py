from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class DisposalGuidelineBase(BaseModel):
    title: str
    instructions: str
    do_not: Optional[str] = None

class DisposalGuidelineResponse(DisposalGuidelineBase):
    id: int
    category_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    is_active: bool

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CategoryDetailResponse(CategoryResponse):
    guidelines: list[DisposalGuidelineResponse] = []

    model_config = ConfigDict(from_attributes=True)
