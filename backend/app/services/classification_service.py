"""Classification service bridging PyTorch, PostgreSQL, and the frontend API."""
import logging
import time
from pathlib import Path

from fastapi import HTTPException, UploadFile
from PIL import Image
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ai.config import get_confidence_level
from app.ai.predictor import Predictor
from app.models.classification import Classification
from app.models.classification_prediction import ClassificationPrediction
from app.models.waste_category import WasteCategory
from app.schemas.classification import (
    ClassificationResponse,
    DisposalResponse,
    HistoryItem,
    HistoryListResponse,
    PredictionItem,
)
from app.services.upload_service import UPLOAD_DIR, UploadService

logger = logging.getLogger(__name__)

# ImageNet labels emitted by the current pretrained model mapped to waste slugs.
# Keep this mapping for selecting the primary waste category and persistence.
WASTE_LABEL_MAPPING: dict[str, str] = {
    "plastic": "plastic",
    "paper": "paper",
    "cardboard": "cardboard",
    "glass": "glass",
    "metal": "metal",
    "organic": "organic",
    "e-waste": "e-waste",
    "other": "other",
    # Legacy ImageNet mappings just in case
    "water bottle": "plastic",
    "pop bottle": "plastic",
    "pill bottle": "plastic",
    "beer bottle": "glass",
    "wine bottle": "glass",
    "paper towel": "paper",
    "envelope": "paper",
    "carton": "cardboard",
    "desktop computer": "e-waste",
    "laptop": "e-waste",
    "mouse": "e-waste",
    "granny smith": "organic",
    "strawberry": "organic",
    "banana": "organic",
    "bell pepper": "organic",
}


BIN_TYPE_MAP: dict[str, str] = {
    "plastic": "Dry / recyclable bin (Blue)",
    "paper": "Dry / recyclable bin (Blue)",
    "cardboard": "Dry / recyclable bin (Blue)",
    "glass": "Glass / bottle bank",
    "metal": "Dry / recyclable bin (Blue)",
    "organic": "Organic / compost bin (Green)",
    "e-waste": "E-waste drop-off / collection point",
    "other": "General residual waste (Black)",
}


def _split_text_to_list(text: str | None) -> list[str]:
    """Convert a guideline paragraph into displayable sentences."""
    if not text:
        return []
    sentences = [sentence.strip() for sentence in text.split(".") if sentence.strip()]
    return sentences or [text.strip()]


def _get_or_fallback_category(db: Session, slug: str) -> WasteCategory | None:
    """Look up a category by slug, falling back to the seeded residual category."""
    category = db.scalars(
        select(WasteCategory).where(WasteCategory.slug == slug)
    ).first()
    if category is None and slug != "other":
        category = db.scalars(
            select(WasteCategory).where(WasteCategory.slug == "other")
        ).first()
    return category


def _confidence_message(level: str) -> str:
    messages = {
        "high": "High-confidence classification",
        "medium": "Moderate-confidence classification",
        "low": "Low-confidence classification — please verify",
    }
    return messages.get(level, "Classification complete")


class ClassificationService:
    @staticmethod
    def classify(image_file: UploadFile, db: Session) -> ClassificationResponse:
        """Upload, infer, persist ranked outputs, and return the frontend schema."""
        upload_result = UploadService.process_upload(image_file)
        filename = upload_result["filename"]
        file_path = UPLOAD_DIR / filename

        try:
            with Image.open(file_path) as image:
                t0 = time.perf_counter()
                prediction_response = Predictor.predict(image)
                inference_ms = int((time.perf_counter() - t0) * 1000)

            predictions_raw = prediction_response.predictions
            if not predictions_raw:
                raise HTTPException(
                    status_code=500,
                    detail="AI prediction returned no results.",
                )

            top_prediction = predictions_raw[0]
            primary_slug = WASTE_LABEL_MAPPING.get(top_prediction.label.strip().lower(), "other")
            category = _get_or_fallback_category(db, primary_slug)
            if category is None:
                raise HTTPException(
                    status_code=422,
                    detail="No valid waste category found in database.",
                )

            try:
                db_classification = Classification(
                    image_filename=filename,
                    image_path=str(file_path),
                    predicted_category_id=category.id,
                    confidence=top_prediction.confidence,
                    model_name=prediction_response.model_name,
                    model_version=prediction_response.model_version,
                )
                db.add(db_classification)
                db.flush()

                for prediction in predictions_raw:
                    prediction_slug = WASTE_LABEL_MAPPING.get(
                        prediction.label.strip().lower(), "other"
                    )
                    prediction_category = _get_or_fallback_category(db, prediction_slug)
                    if prediction_category is None:
                        raise HTTPException(
                            status_code=422,
                            detail="No valid waste category found in database.",
                        )
                    db.add(
                        ClassificationPrediction(
                            classification_id=db_classification.id,
                            category_id=prediction_category.id,
                            rank=prediction.rank,
                            confidence=prediction.confidence,
                        )
                    )

                db.commit()
                db.refresh(db_classification)
            except Exception as exc:
                db.rollback()
                logger.error("Database error during classification: %s", exc)
                if isinstance(exc, HTTPException):
                    raise
                raise HTTPException(
                    status_code=500,
                    detail="Database transaction failed",
                ) from exc

            disposal: DisposalResponse | None = None
            if category.guidelines:
                guideline = category.guidelines[0]
                disposal = DisposalResponse(
                    title=guideline.title,
                    bin_type=BIN_TYPE_MAP.get(category.slug, "General waste bin"),
                    instructions=_split_text_to_list(guideline.instructions),
                    avoid=_split_text_to_list(guideline.do_not),
                )

            shaped_predictions = []
            for prediction in predictions_raw:
                # Preserve the model's actual class name and rank here. Several
                # distinct ImageNet classes map to the same waste slug, so using
                # mapped slugs in this list would falsely duplicate categories.
                logger.debug(
                    "Top-%s model class: class_name=%r confidence=%.6f mapped_slug=%s",
                    prediction.rank,
                    prediction.label,
                    prediction.confidence,
                    WASTE_LABEL_MAPPING.get(prediction.label.strip().lower(), "other"),
                )
                shaped_predictions.append(
                    PredictionItem(
                        category=prediction.label,
                        confidence=prediction.confidence,
                        confidence_level=prediction.confidence_level,
                    )
                )

            confidence_level = get_confidence_level(db_classification.confidence)
            return ClassificationResponse(
                classification_id=db_classification.id,
                category=category.name,
                confidence=db_classification.confidence,
                confidence_level=confidence_level,
                message=_confidence_message(confidence_level),
                predictions=shaped_predictions,
                disposal=disposal,
                inference_ms=inference_ms,
                created_at=db_classification.created_at,
            )
        except HTTPException:
            file_path.unlink(missing_ok=True)
            raise
        except Exception as exc:
            file_path.unlink(missing_ok=True)
            logger.error("Unexpected error during classification: %s", exc)
            raise HTTPException(
                status_code=500,
                detail="Internal server error during classification",
            ) from exc

    @staticmethod
    def get_history(
        db: Session,
        page: int = 1,
        limit: int = 10,
        category: str | None = None,
    ) -> HistoryListResponse:
        """Return paginated classification history, newest first."""
        stmt = select(Classification).order_by(Classification.created_at.desc())
        if category and category.upper() != "ALL":
            stmt = stmt.join(WasteCategory).where(
                func.lower(WasteCategory.name) == category.lower()
            )

        total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        offset = (page - 1) * limit
        rows = db.scalars(stmt.offset(offset).limit(limit)).all()
        items = [
            HistoryItem(
                id=row.id,
                category=row.predicted_category.name,
                confidence=row.confidence,
                confidence_level=get_confidence_level(row.confidence),
                created_at=row.created_at,
                thumbnail=None,
            )
            for row in rows
        ]
        return HistoryListResponse(items=items, total=total, page=page, limit=limit)

    @staticmethod
    def get_history_item(item_id: int, db: Session) -> ClassificationResponse:
        """Retrieve a stored classification using the frontend response contract."""
        row = db.scalars(
            select(Classification).where(Classification.id == item_id)
        ).first()
        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Classification #{item_id} not found",
            )

        category = row.predicted_category
        disposal: DisposalResponse | None = None
        if category.guidelines:
            guideline = category.guidelines[0]
            disposal = DisposalResponse(
                title=guideline.title,
                bin_type=BIN_TYPE_MAP.get(category.slug, "General waste bin"),
                instructions=_split_text_to_list(guideline.instructions),
                avoid=_split_text_to_list(guideline.do_not),
            )

        # Persisted records contain waste-category IDs and ranks, so history
        # returns the category names represented by those database rows.
        shaped_predictions = [
            PredictionItem(
                category=prediction.category.name if prediction.category else category.name,
                confidence=prediction.confidence,
                confidence_level=get_confidence_level(prediction.confidence),
            )
            for prediction in sorted(row.predictions, key=lambda item: item.rank)
        ]
        confidence_level = get_confidence_level(row.confidence)
        return ClassificationResponse(
            classification_id=row.id,
            category=category.name,
            confidence=row.confidence,
            confidence_level=confidence_level,
            message=_confidence_message(confidence_level),
            predictions=shaped_predictions,
            disposal=disposal,
            inference_ms=None,
            created_at=row.created_at,
        )

    @staticmethod
    def get_image_path(item_id: int, db: Session) -> Path:
        """Return the uploaded image path for a classification record."""
        row = db.scalars(
            select(Classification).where(Classification.id == item_id)
        ).first()
        if row is None:
            raise HTTPException(
                status_code=404,
                detail=f"Classification #{item_id} not found",
            )
        path = Path(row.image_path)
        if not path.exists():
            raise HTTPException(status_code=404, detail="Image file not found on disk")
        return path
