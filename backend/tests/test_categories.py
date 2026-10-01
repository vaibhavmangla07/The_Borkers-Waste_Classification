from fastapi.testclient import TestClient

from app.main import app
from app.database.session import get_db

def test_get_categories(client: TestClient):
    response = client.get("/api/categories")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "slug" in data[0]

def test_get_category_by_slug(client: TestClient):
    # we know 'plastic' exists from the seeder
    response = client.get("/api/categories/plastic")
    assert response.status_code == 200
    data = response.json()
    assert data["slug"] == "plastic"

def test_get_category_not_found(client: TestClient):
    response = client.get("/api/categories/nonexistent-category")
    assert response.status_code == 404

def test_get_category_guidance(client: TestClient):
    response = client.get("/api/categories/plastic/guidance")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
