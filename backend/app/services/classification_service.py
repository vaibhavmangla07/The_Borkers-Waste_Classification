from pathlib import Path
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from PIL import Image
import logging

from app.services.upload_service import UploadService, UPLOAD_DIR
from app.ai.predictor import Predictor
from app.ai.config import get_confidence_level
from app.models.waste_category import WasteCategory
from app.models.classification import Classification
from app.models.classification_prediction import ClassificationPrediction
from app.schemas.classification import ClassificationResponse, ClassificationPredictionResponse
from app.schemas.category import CategoryResponse, DisposalGuidelineResponse

logger = logging.getLogger(__name__)

# Very basic mapping from ImageNet to our project's categories
# A proper model would output valid slugs directly.
WASTE_LABEL_MAPPING = {
    # This mapping is required because we are using an ImageNet base model.
    # In a real setup, the fine-tuned model would emit proper slugs.
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
    " Granny Smith": "organic",
    "strawberry": "organic",
    "banana": "organic",
    "bell pepper": "organic",
}

class ClassificationService:
    @staticmethod
    def classify(file: UploadFile, db: Session) -> dict:
        # 1. Process upload
        upload_result = UploadService.process_upload(file)
        filename = upload_result["filename"]
        file_path = UPLOAD_DIR / filename

        try:
            # 2. Open image
            image = Image.open(file_path)

            # 3. Predict
            prediction_response = Predictor.predict(image)
            predictions = prediction_response.predictions

            if not predictions:
                raise HTTPException(status_code=500, detail="AI prediction returned no results.")

            top_prediction = predictions[0]

            # 4. Resolve Category
            raw_label = top_prediction.label.lower()
            mapped_slug = WASTE_LABEL_MAPPING.get(raw_label, "other")

            stmt = select(WasteCategory).where(WasteCategory.slug == mapped_slug)
            category = db.scalars(stmt).first()

            if not category:
                # Fallback to "other" if mapped slug doesn't exist for some reason
                stmt = select(WasteCategory).where(WasteCategory.slug == "other")
                category = db.scalars(stmt).first()
                if not category:
                    raise HTTPException(status_code=422, detail="Valid waste category not found in database.")

            # 5. Save Classification Transaction
            try:
                new_classification = Classification(
                    image_filename=filename,
                    image_path=str(file_path),
                    predicted_category_id=category.id,
                    confidence=top_prediction.confidence,
                    model_name=prediction_response.model_name,
                    model_version=prediction_response.model_version
                )
                db.add(new_classification)
                db.flush() # Get ID

                prediction_responses = []
                for pred in predictions:
                    # Find category for each prediction if possible, else default to 'other'
                    pred_label = pred.label.lower()
                    pred_slug = WASTE_LABEL_MAPPING.get(pred_label, "other")
                    pred_cat_stmt = select(WasteCategory).where(WasteCategory.slug == pred_slug)
                    pred_category = db.scalars(pred_cat_stmt).first()
                    pred_category_id = pred_category.id if pred_category else category.id

                    db_pred = ClassificationPrediction(
                        classification_id=new_classification.id,
                        category_id=pred_category_id,
                        rank=pred.rank,
                        confidence=pred.confidence
                    )
                    db.add(db_pred)
                    
                    prediction_responses.append(
                        ClassificationPredictionResponse(
                            rank=pred.rank,
                            label=pred_slug, # using our slug as label representation in the response
                            confidence=pred.confidence,
                            confidence_level=pred.confidence_level
                        )
                    )

                db.commit()
                db.refresh(new_classification)
            except Exception as e:
                db.rollback()
                logger.error(f"Database error during classification: {e}")
                raise HTTPException(status_code=500, detail="Database transaction failed")

            # 6. Prepare Response
            return {
                "id": new_classification.id,
                "image_filename": new_classification.image_filename,
                "predicted_category": category,
                "confidence": new_classification.confidence,
                "confidence_level": get_confidence_level(new_classification.confidence),
                "model_name": new_classification.model_name,
                "model_version": new_classification.model_version,
                "predictions": prediction_responses,
                "guidance": category.guidelines,
                "created_at": new_classification.created_at
            }
        except HTTPException:
            # Cleanup newly uploaded file
            file_path.unlink(missing_ok=True)
            raise
        except Exception as e:
            file_path.unlink(missing_ok=True)
            logger.error(f"Error during classification: {e}")
            raise HTTPException(status_code=500, detail="Internal server error during classification")
