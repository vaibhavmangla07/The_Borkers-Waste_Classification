# EcoVision AI Backend

Backend for the EcoVision AI waste classification platform.

Stack:

- FastAPI
- PostgreSQL
- PyTorch
- Docker
- Kubernetes
- Helm

The backend is being developed phase-by-phase.

## Phase 2: FastAPI Initialization

Project:
EcoVision AI

Backend:
FastAPI

### Run locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

### Endpoints & Documentation:

- **API Root**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## Phase 4: Database Models, Alembic Migrations & Seed Data

### Database
PostgreSQL

### ORM
SQLAlchemy

### Migration Tool
Alembic

### Migration Commands

```bash
alembic revision --autogenerate -m "migration message"
alembic upgrade head
alembic downgrade -1
```

### Seed

```bash
python scripts/seed.py
```

---

## Phase 5: Pydantic Schemas + Categories API

### New Endpoints
- **GET** `/api/categories` - Get all waste categories
- **GET** `/api/categories/{slug}` - Get a category by its slug
- **GET** `/api/categories/{slug}/guidance` - Get disposal guidance for a category

---

## Phase 6: Image Upload & Validation

### Image Upload API
- **POST** `/api/upload` - Upload an image for waste classification

**Content-Type:** `multipart/form-data`
**Field:** `file`

**Supported Formats:** JPEG, PNG, WEBP
**Maximum Size:** 10 MB

**Example Response:**
```json
{
    "filename": "generated-uuid.jpg",
    "original_filename": "plastic-bottle.jpg",
    "content_type": "image/jpeg",
    "size_bytes": 245123,
    "width": 640,
    "height": 480,
    "message": "Image uploaded successfully"
}
```

*Note: Phase 6 only validates and stores the image locally. AI classification will be added in Phase 7.*

---

## Phase 7: PyTorch AI Module & Pretrained Vision Model

### AI
**Framework:** PyTorch  
**Vision:** torchvision  
**Model:** MobileNetV3 Small (Lightweight pretrained model)  
**Inference:** Local execution  
**Device Support:** CUDA / MPS / CPU  
**Top-K:** 3 predictions returned  

*Important note: The current pretrained model is an AI pipeline foundation to establish local inference correctly without relying on cloud services. The final waste-category classifier will use a project-specific fine-tuned model.*

---

## Phase 8: End-to-End Waste Classification API

### Classification API
- **POST** `/api/classify` - Upload and classify an image in one step

**Content-Type:** `multipart/form-data`
**Field:** `file`

**Example Response:**
```json
{
    "id": 1,
    "image_filename": "uuid.jpg",
    "predicted_category": {
        "id": 1,
        "name": "Plastic",
        "slug": "plastic",
        "description": "...",
        "is_active": true,
        "created_at": "...",
        "updated_at": "..."
    },
    "confidence": 0.95,
    "confidence_level": "high",
    "model_name": "mobilenet_v3_small",
    "model_version": "0.1.0",
    "predictions": [
        {
            "rank": 1,
            "label": "plastic",
            "confidence": 0.95,
            "confidence_level": "high"
        }
    ],
    "guidance": [
        {
            "id": 1,
            "category_id": 1,
            "title": "Plastic Disposal",
            "instructions": "Rinse before recycling",
            "do_not": "Do not put plastic bags in the bin",
            "created_at": "...",
            "updated_at": "..."
        }
    ],
    "created_at": "..."
}
```




