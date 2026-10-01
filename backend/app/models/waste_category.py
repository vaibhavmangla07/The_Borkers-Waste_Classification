from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.classification import Classification
    from app.models.classification_prediction import ClassificationPrediction
    from app.models.disposal_guideline import DisposalGuideline


class WasteCategory(Base):
    __tablename__ = "waste_categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    guidelines: Mapped[List["DisposalGuideline"]] = relationship(
        "DisposalGuideline", back_populates="category", cascade="all, delete-orphan"
    )
    classifications: Mapped[List["Classification"]] = relationship(
        "Classification", back_populates="predicted_category"
    )
    predictions: Mapped[List["ClassificationPrediction"]] = relationship(
        "ClassificationPrediction", back_populates="category"
    )

    def __repr__(self) -> str:
        return f"<WasteCategory(id={self.id}, name='{self.name}', slug='{self.slug}')>"
