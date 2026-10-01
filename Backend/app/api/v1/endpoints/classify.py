import time
from typing import List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.db.session import get_db
from app.models.classification import WasteScan
from app.schemas.classification import (
    BatchClassificationResponse,
    CategoryInfo,
    WasteScanResponse,
)
from app.services.classifier import classifier_service
from app.services.storage import storage_service

router = APIRouter()


@router.get(
    "/categories",
    response_model=List[CategoryInfo],
    summary="List Waste Categories & Disposal Rules"
)
async def list_categories():
    """
    Returns full metadata for all recognized waste classification categories,
    including designated bin colors, descriptions, common items, and disposal rules.
    """
    return classifier_service.get_categories()


@router.post(
    "",
    response_model=WasteScanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Classify Waste Image"
)
async def classify_image(
    file: UploadFile = File(..., description="Image file of waste item (JPEG, PNG, WebP)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Accepts an uploaded image file, performs waste classification inference,
    records the scan in the database, and returns the classification results along
    with disposal guidelines and eco tips.
    """
    start_time = time.time()

    # Save to storage and validate image
    stored_filename, image_url, file_size, img_format = await storage_service.save_upload(file)

    # Read image bytes for inference
    await file.seek(0)
    image_bytes = await file.read()

    # Run inference
    try:
        prediction = classifier_service.predict(image_bytes, filename=file.filename or "")
    except Exception as e:
        logger.error(f"Inference error on {file.filename}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run inference on image: {str(e)}"
        )

    processing_time_ms = round((time.time() - start_time) * 1000, 2)

    # Persist in database
    scan_record = WasteScan(
        original_filename=file.filename or "unknown.jpg",
        stored_filename=stored_filename,
        image_url=image_url,
        category=prediction.category.value,
        item_name=prediction.item_name,
        confidence=prediction.confidence,
        recyclable=prediction.recyclable,
        bin_color=prediction.bin_color,
        disposal_guidance=prediction.disposal_guidance,
        eco_tip=prediction.eco_tip,
        image_format=img_format,
        file_size_bytes=file_size,
        processing_time_ms=processing_time_ms
    )

    db.add(scan_record)
    await db.commit()
    await db.refresh(scan_record)

    logger.info(
        f"Classified '{file.filename}' -> {prediction.category.value} "
        f"({prediction.item_name}, {prediction.confidence:.2f}) in {processing_time_ms}ms"
    )

    return scan_record


@router.post(
    "/batch",
    response_model=BatchClassificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Batch Classify Multiple Images"
)
async def batch_classify(
    files: List[UploadFile] = File(..., description="List of waste images (up to 10 files)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Processes multiple image uploads in a single batch.
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum batch limit is 10 images per request."
        )

    successful_results: List[WasteScanResponse] = []
    errors: List[dict] = []

    for file in files:
        try:
            start_time = time.time()
            stored_filename, image_url, file_size, img_format = await storage_service.save_upload(file)

            await file.seek(0)
            image_bytes = await file.read()
            prediction = classifier_service.predict(image_bytes, filename=file.filename or "")
            processing_time_ms = round((time.time() - start_time) * 1000, 2)

            scan_record = WasteScan(
                original_filename=file.filename or "unknown.jpg",
                stored_filename=stored_filename,
                image_url=image_url,
                category=prediction.category.value,
                item_name=prediction.item_name,
                confidence=prediction.confidence,
                recyclable=prediction.recyclable,
                bin_color=prediction.bin_color,
                disposal_guidance=prediction.disposal_guidance,
                eco_tip=prediction.eco_tip,
                image_format=img_format,
                file_size_bytes=file_size,
                processing_time_ms=processing_time_ms
            )
            db.add(scan_record)
            await db.commit()
            await db.refresh(scan_record)

            successful_results.append(WasteScanResponse.model_validate(scan_record))
        except Exception as e:
            errors.append({"filename": file.filename or "unknown", "error": str(e)})

    return BatchClassificationResponse(
        total_processed=len(files),
        successful=len(successful_results),
        failed=len(errors),
        results=successful_results,
        errors=errors
    )
