from datetime import datetime, timezone
from typing import TYPE_CHECKING, List
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.classification_prediction import ClassificationPrediction
    from app.models.waste_category import WasteCategory


class Classification(Base):
    __tablename__ = "classifications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    image_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    predicted_category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("waste_categories.id"),
        nullable=False,
        index=True,
    )
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    predicted_category: Mapped["WasteCategory"] = relationship(
        "WasteCategory", back_populates="classifications"
    )
    predictions: Mapped[List["ClassificationPrediction"]] = relationship(
        "ClassificationPrediction",
        back_populates="classification",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Classification(id={self.id}, image='{self.image_filename}', confidence={self.confidence:.4f})>"
