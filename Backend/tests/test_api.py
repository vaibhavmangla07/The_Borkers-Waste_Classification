import io
import pytest
from httpx import ASGITransport, AsyncClient
from PIL import Image

from app.db.session import init_db
from app.main import app


import asyncio

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Ensure database schema is created prior to running tests."""
    asyncio.run(init_db())


def create_test_image(color=(34, 139, 34), format_name="PNG") -> bytes:
    """Generates an in-memory test image."""
    img = Image.new("RGB", (100, 100), color=color)
    buf = io.BytesIO()
    img.save(buf, format=format_name)
    return buf.getvalue()


@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "documentation" in data


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "version" in data


@pytest.mark.asyncio
async def test_categories_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/classify/categories")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 4
        categories = {item["category"] for item in data}
        assert "organic" in categories
        assert "recyclable" in categories
        assert "hazardous" in categories
        assert "non_recyclable" in categories


@pytest.mark.asyncio
async def test_classify_and_history_lifecycle():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Upload valid image
        image_bytes = create_test_image(color=(46, 125, 50))  # Greenish image
        files = {
            "file": ("test_leaf.png", image_bytes, "image/png")
        }
        res = await client.post("/api/v1/classify", files=files)
        assert res.status_code == 201
        scan_data = res.json()
        assert "id" in scan_data
        scan_id = scan_data["id"]
        assert scan_data["confidence"] > 0
        assert scan_data["bin_color"] is not None
        assert scan_data["disposal_guidance"] is not None

        # 2. Verify in history
        history_res = await client.get("/api/v1/history")
        assert history_res.status_code == 200
        history_data = history_res.json()
        assert history_data["total"] >= 1
        ids = [item["id"] for item in history_data["items"]]
        assert scan_id in ids

        # 3. Check stats
        stats_res = await client.get("/api/v1/history/stats")
        assert stats_res.status_code == 200
        stats = stats_res.json()
        assert stats["total_scans"] >= 1
        assert len(stats["category_breakdown"]) > 0

        # 4. Get by ID
        detail_res = await client.get(f"/api/v1/history/{scan_id}")
        assert detail_res.status_code == 200
        assert detail_res.json()["id"] == scan_id

        # 5. Delete scan
        del_res = await client.delete(f"/api/v1/history/{scan_id}")
        assert del_res.status_code == 204

        # 6. Confirm deleted
        get_deleted = await client.get(f"/api/v1/history/{scan_id}")
        assert get_deleted.status_code == 404


@pytest.mark.asyncio
async def test_invalid_file_extension():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        files = {
            "file": ("document.txt", b"plain text", "text/plain")
        }
        res = await client.post("/api/v1/classify", files=files)
        assert res.status_code == 415


@pytest.mark.asyncio
async def test_batch_classify():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        img1 = create_test_image(color=(30, 144, 255))
        img2 = create_test_image(color=(220, 20, 60))
        files = [
            ("files", ("bottle.png", img1, "image/png")),
            ("files", ("battery.png", img2, "image/png"))
        ]
        res = await client.post("/api/v1/classify/batch", files=files)
        assert res.status_code == 200
        data = res.json()
        assert data["total_processed"] == 2
        assert data["successful"] == 2
        assert len(data["results"]) == 2
