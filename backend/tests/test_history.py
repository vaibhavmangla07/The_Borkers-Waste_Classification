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
def test_classifications():
    db_session = SessionLocal()
    try:
        # Setup: we need some WasteCategory
        stmt = select(WasteCategory)
        categories = db_session.scalars(stmt).all()
        if not categories:
            pytest.skip("No categories found in database")
            
        plastic_cat = next((c for c in categories if c.slug == "plastic"), categories[0])
        paper_cat = next((c for c in categories if c.slug == "paper"), categories[1] if len(categories) > 1 else categories[0])

        classifications = []
        # Create 5 classifications (3 plastic, 2 paper)
        for i in range(5):
            cat = plastic_cat if i < 3 else paper_cat
            c = Classification(
                image_filename=f"test_image_{i}.jpg",
                image_path=f"storage/uploads/test_image_{i}.jpg",
                predicted_category_id=cat.id,
                confidence=0.9 - (i * 0.1),
                model_name="mock_model",
                model_version="0.1.0"
            )
            db_session.add(c)
            db_session.flush()
            
            # Add predictions
            p1 = ClassificationPrediction(
                classification_id=c.id,
                category_id=cat.id,
                rank=1,
                confidence=c.confidence
            )
            db_session.add(p1)
            classifications.append(c)
            
        db_session.commit()
        
        yield classifications
        
        # Cleanup
        for c in classifications:
            db_session.delete(c)
        db_session.commit()
    finally:
        db_session.close()

def test_get_history_empty():
    response = client.get("/api/history")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    # Might not be empty if other tests ran, but let's just check format
    assert isinstance(data["items"], list)
    assert data["page"] == 1
    assert data["limit"] == 10

def test_get_history_pagination(test_classifications):
    response = client.get("/api/history?page=1&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] >= 5
    assert data["page"] == 1
    assert data["limit"] == 2
    
    # check newest first
    item1 = data["items"][0]
    item2 = data["items"][1]
    assert item1["id"] > item2["id"] # assuming monotonic creation

    response2 = client.get("/api/history?page=2&limit=2")
    data2 = response2.json()
    assert len(data2["items"]) == 2
    assert data2["items"][0]["id"] < item2["id"]

def test_get_history_category_filter(test_classifications):
    response = client.get("/api/history?category=plastic")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 3
    for item in data["items"]:
        assert item["category"].lower() == "plastic"

def test_get_history_invalid_category():
    response = client.get("/api/history?category=invalid-category-xyz")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 0

def test_get_history_detail(test_classifications):
    target_id = test_classifications[0].id
    response = client.get(f"/api/history/{target_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["classification_id"] == target_id
    assert "category" in data
    assert "predictions" in data
    assert len(data["predictions"]) > 0

def test_get_history_detail_not_found():
    response = client.get("/api/history/99999999")
    assert response.status_code == 404
