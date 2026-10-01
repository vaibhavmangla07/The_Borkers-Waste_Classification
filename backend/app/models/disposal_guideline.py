from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.waste_category import WasteCategory


class DisposalGuideline(Base):
    __tablename__ = "disposal_guidelines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("waste_categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    do_not: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
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
    category: Mapped["WasteCategory"] = relationship(
        "WasteCategory", back_populates="guidelines"
    )

    def __repr__(self) -> str:
        return f"<DisposalGuideline(id={self.id}, title='{self.title}', category_id={self.category_id})>"
