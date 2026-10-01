import io
import pytest
from pathlib import Path
from PIL import Image
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.prediction import PredictionResponse, PredictionResult
from app.models.classification import Classification
from app.models.classification_prediction import ClassificationPrediction
from app.database.session import get_db

client = TestClient(app)

def create_test_image(format="JPEG", size=(100, 100), color="blue"):
    file_obj = io.BytesIO()
    image = Image.new("RGB", size, color=color)
    image.save(file_obj, format=format)
    file_obj.seek(0)
    return file_obj

@pytest.fixture
def mock_predictor():
    with patch("app.services.classification_service.Predictor") as mock:
        mock.predict.return_value = PredictionResponse(
            model_name="mock_model",
            model_version="0.1.0",
            device="cpu",
            predictions=[
                PredictionResult(rank=1, label="plastic", confidence=0.95, confidence_level="high"),
                PredictionResult(rank=2, label="paper", confidence=0.03, confidence_level="low"),
                PredictionResult(rank=3, label="e-waste", confidence=0.02, confidence_level="low"),
            ]
        )
        yield mock

def test_classify_image_success(mock_predictor):
    img_bytes = create_test_image("JPEG")
    response = client.post(
        "/api/classify",
        files={"image": ("test_classify.jpg", img_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "classification_id" in data
    assert data["category"] == "Plastic"
    assert data["confidence"] == 0.95
    assert len(data["predictions"]) == 3
    assert data["predictions"][0]["category"] == "plastic"
    assert data["predictions"][1]["category"] == "paper"
    assert data["predictions"][2]["category"] == "e-waste"
    assert data["disposal"] is not None

    # cleanup DB and image
    db = next(get_db())
    c = db.query(Classification).filter(Classification.id == data["classification_id"]).first()
    if c:
        full_path = Path(c.image_path)
        if full_path.exists():
            full_path.unlink()
        db.query(ClassificationPrediction).filter(ClassificationPrediction.classification_id == c.id).delete()
        db.delete(c)
        db.commit()

def test_classify_invalid_image():
    response = client.post(
        "/api/classify",
        files={"image": ("fake.jpg", io.BytesIO(b"Not an image"), "image/jpeg")}
    )
    assert response.status_code == 400

@patch("app.services.classification_service.Predictor")
def test_classify_ai_failure(mock_predictor):
    mock_predictor.predict.side_effect = Exception("AI failure")
    
    img_bytes = create_test_image("JPEG")
    response = client.post(
        "/api/classify",
        files={"image": ("test_fail.jpg", img_bytes, "image/jpeg")}
    )
    assert response.status_code == 500
    
    # check that file is cleaned up
    # wait, we can't easily check the filename since it's random, but we can verify our upload dir doesn't grow
    
@patch("app.services.classification_service.Predictor")
def test_classify_unknown_category(mock_predictor):
    mock_predictor.predict.return_value = PredictionResponse(
        model_name="mock_model",
        model_version="0.1.0",
        device="cpu",
        predictions=[
            PredictionResult(rank=1, label="unknown_random_thing", confidence=0.95, confidence_level="high"),
        ]
    )
    
    img_bytes = create_test_image("JPEG")
    response = client.post(
        "/api/classify",
        files={"image": ("test_unknown.jpg", img_bytes, "image/jpeg")}
    )
    # the mapping defaults to 'other', so it should succeed
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "Other"
    
    db = next(get_db())
    c = db.query(Classification).filter(Classification.id == data["classification_id"]).first()
    if c:
        full_path = Path(c.image_path)
        if full_path.exists():
            full_path.unlink()
        db.query(ClassificationPrediction).filter(ClassificationPrediction.classification_id == c.id).delete()
        db.delete(c)
        db.commit()
