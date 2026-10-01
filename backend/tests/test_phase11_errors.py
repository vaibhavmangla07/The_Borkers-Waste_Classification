import pytest
import io
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app

client = TestClient(app, raise_server_exceptions=False)

def test_unknown_route():
    response = client.get("/nope")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"

def test_validation_error():
    response = client.get("/api/history?page=abc")
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"

def test_oversized_request():
    # Simulate a request where Content-Length exceeds max_bytes (default 10MB)
    response = client.post(
        "/api/upload",
        content=b"A" * 10,
        headers={"Content-Length": str(15 * 1024 * 1024)} # 15 MB
    )
    assert response.status_code == 413
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "FILE_TOO_LARGE"

def test_cors_header():
    response = client.options(
        "/api/categories",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"

def test_sql_injection_like_category_input():
    response = client.get("/api/history?category=' OR 1=1 --")
    # Our category filtering uses parameterized queries via SQLAlchemy
    # It should not break the syntax but instead not find the category (404)
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"

def test_invalid_upload():
    response = client.post(
        "/api/upload",
        files={"file": ("fake.jpg", io.BytesIO(b"Not an image"), "image/jpeg")}
    )
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "HTTP_ERROR"

def test_corrupted_image():
    # Similar to invalid upload
    response = client.post(
        "/api/upload",
        files={"file": ("corrupted.jpg", io.BytesIO(b"\xff\xd8\xff\xe0\x00\x10\x4a\x46\x49\x46\x00\x01"), "image/jpeg")}
    )
    assert response.status_code == 400
    data = response.json()
    assert "error" in data

def test_invalid_history_parameters():
    response = client.get("/api/history?page_size=0")
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"

    response = client.get("/api/history?page_size=1000")
    assert response.status_code == 422

@patch("app.routes.categories.CategoryService.get_categories")
def test_unexpected_exception_handling(mock_service):
    mock_service.side_effect = Exception("Some weird bug")
    response = client.get("/api/categories")
    assert response.status_code == 500
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "INTERNAL_ERROR"

from sqlalchemy.exc import SQLAlchemyError

@patch("app.routes.categories.CategoryService.get_categories")
def test_database_error_handling(mock_service):
    mock_service.side_effect = SQLAlchemyError("DB down")
    response = client.get("/api/categories")
    assert response.status_code == 500
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "DATABASE_ERROR"
