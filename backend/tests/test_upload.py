import io
from pathlib import Path
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app

def create_test_image(format="JPEG", size=(100, 100), color="red"):
    file_obj = io.BytesIO()
    image = Image.new("RGB", size, color=color)
    image.save(file_obj, format=format)
    file_obj.seek(0)
    return file_obj

def test_upload_valid_jpeg(client: TestClient):
    img_bytes = create_test_image("JPEG")
    response = client.post(
        "/api/upload",
        files={"file": ("test.jpg", img_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content_type"] == "image/jpeg"
    assert data["width"] == 100
    assert data["height"] == 100
    
    # cleanup
    file_path = Path("storage/uploads") / data["filename"]
    if file_path.exists():
        file_path.unlink()

def test_upload_valid_png(client: TestClient):
    img_bytes = create_test_image("PNG")
    response = client.post(
        "/api/upload",
        files={"file": ("test.png", img_bytes, "image/png")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content_type"] == "image/png"
    assert data["width"] == 100
    assert data["height"] == 100
    
    # cleanup
    file_path = Path("storage/uploads") / data["filename"]
    if file_path.exists():
        file_path.unlink()

def test_upload_valid_webp(client: TestClient):
    img_bytes = create_test_image("WEBP")
    response = client.post(
        "/api/upload",
        files={"file": ("test.webp", img_bytes, "image/webp")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content_type"] == "image/webp"
    
    # cleanup
    file_path = Path("storage/uploads") / data["filename"]
    if file_path.exists():
        file_path.unlink()

def test_upload_empty_file(client: TestClient):
    response = client.post(
        "/api/upload",
        files={"file": ("empty.jpg", io.BytesIO(b""), "image/jpeg")}
    )
    assert response.status_code == 400

def test_upload_invalid_file(client: TestClient):
    response = client.post(
        "/api/upload",
        files={"file": ("test.txt", io.BytesIO(b"This is not an image"), "text/plain")}
    )
    assert response.status_code == 400

def test_upload_fake_image(client: TestClient):
    response = client.post(
        "/api/upload",
        files={"file": ("fake.jpg", io.BytesIO(b"This is not an image"), "image/jpeg")}
    )
    assert response.status_code == 400

def test_upload_oversized_file(client: TestClient):
    # Mock a large file by sending just bytes over the limit, it will trigger the size check before reading
    # Since we read the whole content into memory for validation, we'll just send 10MB + 1 byte
    large_content = b"0" * (10 * 1024 * 1024 + 1)
    response = client.post(
        "/api/upload",
        files={"file": ("large.jpg", io.BytesIO(large_content), "image/jpeg")}
    )
    assert response.status_code == 413
