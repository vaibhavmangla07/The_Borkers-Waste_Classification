from sqlalchemy import String, Float, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class WasteScan(Base, TimestampMixin):
    """SQLAlchemy model for storing waste classification scans."""
    __tablename__ = "waste_scans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    image_url: Mapped[str] = mapped_column(String(512), nullable=False)
    
    # Classification results
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    item_name: Mapped[str] = mapped_column(String(100), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    recyclable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    # Actionable guidance
    bin_color: Mapped[str] = mapped_column(String(30), nullable=False, default="Black")
    disposal_guidance: Mapped[str] = mapped_column(Text, nullable=False)
    eco_tip: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Metadata
    image_format: Mapped[str] = mapped_column(String(20), nullable=True)
    file_size_bytes: Mapped[int] = mapped_column(nullable=False, default=0)
    processing_time_ms: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    def __repr__(self) -> str:
        return f"<WasteScan(id={self.id}, item='{self.item_name}', category='{self.category}', confidence={self.confidence:.2f})>"
