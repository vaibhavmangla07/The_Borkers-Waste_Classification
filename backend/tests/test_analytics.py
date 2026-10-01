import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.models.classification import Classification
from app.models.classification_prediction import ClassificationPrediction
from app.models.waste_category import WasteCategory
from app.database.session import SessionLocal

client = TestClient(app)

@pytest.fixture
def test_analytics_classifications():
    db_session = SessionLocal()
    try:
        stmt = select(WasteCategory)
        categories = db_session.scalars(stmt).all()
        if not categories:
            pytest.skip("No categories found in database")
            
        plastic_cat = next((c for c in categories if c.slug == "plastic"), categories[0])
        paper_cat = next((c for c in categories if c.slug == "paper"), categories[1] if len(categories) > 1 else categories[0])
        
        # Test requires: Plastic: 0.90, 0.85, 0.70; Paper: 0.65, 0.55; Glass: 0.40
        # If we don't have glass, we'll use organic or e-waste. Let's find a third one.
        glass_cat = next((c for c in categories if c.slug == "glass"), categories[2] if len(categories) > 2 else categories[0])

        confidences = [
            (plastic_cat, 0.90),
            (plastic_cat, 0.85),
            (plastic_cat, 0.70),
            (paper_cat, 0.65),
            (paper_cat, 0.55),
            (glass_cat, 0.40)
        ]

        classifications = []
        for i, (cat, conf) in enumerate(confidences):
            c = Classification(
                image_filename=f"analytics_test_{i}.jpg",
                image_path=f"storage/uploads/analytics_test_{i}.jpg",
                predicted_category_id=cat.id,
                confidence=conf,
                model_name="mock_model",
                model_version="0.1.0"
            )
            db_session.add(c)
            db_session.flush()
            classifications.append(c)
            
        db_session.commit()
        
        yield classifications
        
        # Cleanup
        for c in classifications:
            db_session.delete(c)
        db_session.commit()
    finally:
        db_session.close()

def test_analytics_summary_empty():
    response = client.get("/api/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_classifications"] == 0
    assert data["average_confidence"] == 0.0
    assert data["most_classified_category"] is None
    assert data["high_confidence_count"] == 0
    assert data["medium_confidence_count"] == 0
    assert data["low_confidence_count"] == 0

def test_analytics_categories_empty():
    response = client.get("/api/analytics/categories")
    assert response.status_code == 200
    data = response.json()
    assert data["total_classifications"] == 0
    assert len(data["items"]) > 0  # should still list active categories
    for item in data["items"]:
        assert item["classification_count"] == 0
        assert item["percentage"] == 0.0

def test_analytics_recent_empty():
    response = client.get("/api/analytics/recent")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []

def test_analytics_summary(test_analytics_classifications):
    response = client.get("/api/analytics/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_classifications"] == 6
    assert data["total_categories"] > 0
    assert data["most_classified_category"]["slug"] == "plastic"
    assert data["most_classified_category"]["count"] == 3
    
    # average of [0.90, 0.85, 0.70, 0.65, 0.55, 0.40] = 4.05 / 6 = 0.675
    assert abs(data["average_confidence"] - 0.675) < 0.001
    
    # high: >=0.80 -> 2 (0.90, 0.85)
    assert data["high_confidence_count"] == 2
    # medium: >=0.60 and <0.80 -> 2 (0.70, 0.65)
    assert data["medium_confidence_count"] == 2
    # low: <0.60 -> 2 (0.55, 0.40)
    assert data["low_confidence_count"] == 2

def test_analytics_category_distribution(test_analytics_classifications):
    response = client.get("/api/analytics/categories")
    assert response.status_code == 200
    data = response.json()
    assert data["total_classifications"] == 6
    
    plastic = next(i for i in data["items"] if i["category_slug"] == "plastic")
    assert plastic["classification_count"] == 3
    assert plastic["percentage"] == 50.0
    
    paper = next(i for i in data["items"] if i["category_slug"] == "paper")
    assert paper["classification_count"] == 2
    # 2/6 = 33.33%
    assert abs(paper["percentage"] - 33.33) < 0.01

    glass = next(i for i in data["items"] if i["category_slug"] == "glass")
    assert glass["classification_count"] == 1
    # 1/6 = 16.67%
    assert abs(glass["percentage"] - 16.67) < 0.01

    organic = next((i for i in data["items"] if i["category_slug"] == "organic"), None)
    if organic:
        assert organic["classification_count"] == 0
        assert organic["percentage"] == 0.0

def test_analytics_recent(test_analytics_classifications):
    response = client.get("/api/analytics/recent?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    # latest inserted should be index 5, then index 4 (from test fixture)
    assert data["items"][0]["confidence"] == 0.40
    assert data["items"][1]["confidence"] == 0.55

def test_analytics_recent_invalid_limit():
    response = client.get("/api/analytics/recent?limit=0")
    assert response.status_code == 422
    
    response = client.get("/api/analytics/recent?limit=51")
    assert response.status_code == 422
