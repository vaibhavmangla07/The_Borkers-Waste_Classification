from typing import TYPE_CHECKING
from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.classification import Classification
    from app.models.waste_category import WasteCategory


class ClassificationPrediction(Base):
    __tablename__ = "classification_predictions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    classification_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("classifications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("waste_categories.id"),
        nullable=False,
        index=True,
    )
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    # Relationships
    classification: Mapped["Classification"] = relationship(
        "Classification", back_populates="predictions"
    )
    category: Mapped["WasteCategory"] = relationship(
        "WasteCategory", back_populates="predictions"
    )

    def __repr__(self) -> str:
        return f"<ClassificationPrediction(id={self.id}, classification_id={self.classification_id}, rank={self.rank}, confidence={self.confidence:.4f})>"
