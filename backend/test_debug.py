import io
from fastapi.testclient import TestClient
from app.main import app
from PIL import Image

def create_test_image(format="JPEG"):
    img = Image.new("RGB", (100, 100), color="red")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format=format)
    return img_byte_arr.getvalue()

client = TestClient(app)
img_bytes = create_test_image("JPEG")
response = client.post("/api/classify", files={"file": ("test_classify.jpg", img_bytes, "image/jpeg")})
print(response.json())
