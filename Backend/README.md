# ♻️ Waste Classification API

A high-performance, asynchronous REST API for real-time waste image classification, recycling guidance, and history analytics. Built with **FastAPI**, **Pydantic v2**, and **SQLAlchemy (Async)**.

---

## 🚀 Key Features

- **⚡ Asynchronous & Fast**: Powered by `uvicorn` and `asyncio` for non-blocking I/O.
- **📷 Image Classification Pipeline**: Supports single & batch waste image scanning (JPEG, PNG, WebP) with validation, size guards, and processing telemetry.
- **🏷️ Multi-Category Waste Taxonomy**:
  - 🟢 **Organic / Compostable**: Food scraps, vegetable waste, yard trimmings (Green Bin).
  - 🔵 **Recyclable**: Rigid plastics, cardboard, paper, glass, aluminium cans (Blue Bin).
  - 🔴 **Hazardous / E-Waste**: Batteries, fluorescent bulbs, aerosol cans, electronics (Red Bin / Drop-off).
  - ⚫ **Residual / Landfill**: Greasy containers, composite wrappers, non-recyclables (Black Bin).
- **💾 Database Persistence**: Tracks scan history, detected items, confidence metrics, and processing time using SQLite (or PostgreSQL).
- **📊 Analytics & Metrics**: Aggregated recycling rate calculations, category breakdowns, and average confidence stats.
- **🔌 Pluggable ML Engine**: Drop in an ONNX (`.onnx`) or PyTorch (`.pt`) model file into `models/` or customize the pipeline in `app/services/classifier.py`.
- **📖 Interactive API Docs**: Auto-generated Swagger UI (`/docs`) and ReDoc (`/redoc`).

---

## 📂 Project Architecture

```
Backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── classify.py      # /api/v1/classify & /api/v1/classify/batch
│   │   │   │   ├── history.py       # /api/v1/history & /api/v1/history/stats
│   │   │   │   └── health.py        # /api/v1/health
│   │   │   └── router.py            # Aggregated v1 router
│   ├── core/
│   │   ├── config.py                # Pydantic Settings & environment config
│   │   └── logging.py               # Structured logger
│   ├── db/
│   │   ├── base.py                  # SQLAlchemy DeclarativeBase
│   │   └── session.py               # Async engine and session factory
│   ├── models/
│   │   └── classification.py        # SQLAlchemy WasteScan model
│   ├── schemas/
│   │   ├── classification.py        # Pydantic request/response schemas
│   │   └── health.py                # Healthcheck schema
│   ├── services/
│   │   ├── classifier.py            # ML inference & feature extraction service
│   │   └── storage.py               # Upload validation & storage service
│   ├── static/
│   │   └── uploads/                 # Uploaded images store
│   └── main.py                      # FastAPI application entrypoint
├── tests/
│   └── test_api.py                  # Pytest test suite
├── .env.example                     # Environment variables template
├── Dockerfile                       # Container deployment definition
├── docker-compose.yml               # Local Docker service setup
└── requirements.txt                 # Python dependencies
```

---

## 🛠️ Quick Start

### Option 1: Local Virtual Environment

1. **Navigate to the Backend directory**:
   ```bash
   cd Backend
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```

5. **Start the development server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access Interactive Docs**:
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### Option 2: Docker / Docker Compose

```bash
cd Backend
docker compose up --build
```

The API will be available at `http://localhost:8000`.

---

## 📡 API Endpoints Overview

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Root status and links |
| `GET` | `/api/v1/health` | Healthcheck and DB status |
| `GET` | `/api/v1/classify/categories` | List waste categories & disposal guidelines |
| `POST` | `/api/v1/classify` | Upload and classify a single waste image |
| `POST` | `/api/v1/classify/batch` | Batch classify multiple images (up to 10) |
| `GET` | `/api/v1/history` | Paginated scan history (supports filters) |
| `GET` | `/api/v1/history/stats` | Aggregated recycling statistics |
| `GET` | `/api/v1/history/{id}` | Retrieve single scan details |
| `DELETE` | `/api/v1/history/{id}` | Delete scan and associated image file |

---

## 🧪 Example Requests

### 1. Classify an Image (cURL)
```bash
curl -X POST "http://localhost:8000/api/v1/classify" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/bottle.jpg;type=image/jpeg"
```

**Response (HTTP 201 Created)**:
```json
{
  "id": 1,
  "original_filename": "bottle.jpg",
  "stored_filename": "550e8400e29b41d4a716446655440000.jpg",
  "image_url": "/static/uploads/550e8400e29b41d4a716446655440000.jpg",
  "category": "recyclable",
  "item_name": "PET Plastic Bottle",
  "confidence": 0.94,
  "recyclable": true,
  "bin_color": "Blue",
  "disposal_guidance": "Empty all liquids and scrape off food residue.",
  "eco_tip": "Recycling one plastic bottle saves enough energy to power a 60W lightbulb for 3 hours.",
  "file_size_bytes": 1048576,
  "processing_time_ms": 32.4,
  "created_at": "2026-10-01T04:10:00Z"
}
```

### 2. Get Historical Analytics (cURL)
```bash
curl -X GET "http://localhost:8000/api/v1/history/stats"
```

---

## 🧪 Running Automated Tests

Run the test suite with `pytest`:

```bash
cd Backend
pytest tests/ -v
```

---

## 🤖 Custom Machine Learning Model Integration

To plug in your custom model:
1. Export your trained model to ONNX format (e.g. `waste_classifier.onnx`) or PyTorch (`.pt`).
2. Place the file inside `Backend/models/waste_classifier.onnx`.
3. Set `MODEL_PATH="./models/waste_classifier.onnx"` in your `.env` file.
4. Customize any model-specific input preprocessing in [`app/services/classifier.py`](file:///Users/vmangla/Documents/Vaibhav/The_Brokers-Waste_Classification/Backend/app/services/classifier.py).
