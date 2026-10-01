from fastapi.testclient import TestClient


def test_read_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to EcoVision AI API"}


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_openapi_schema(client: TestClient):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert data["info"]["title"] == "EcoVision AI"
    assert data["info"]["version"] == "0.1.0"


def test_models_and_metadata():
    """Verify that all models import cleanly and register their expected tables."""
    from app.database.base import Base
    import app.models  # noqa: F401

    expected_tables = {
        "waste_categories",
        "disposal_guidelines",
        "classifications",
        "classification_predictions",
    }
    assert expected_tables.issubset(set(Base.metadata.tables.keys()))
