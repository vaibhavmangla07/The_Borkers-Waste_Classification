# EcoVision AI Backend

## Stack

Python 3.11
FastAPI
PostgreSQL
SQLAlchemy
Alembic
PyTorch
Docker

## Environment

Configure these environment variables in a `.env` file (see `.env.example`):

- `DATABASE_URL`: e.g. `postgresql+psycopg://username:password@localhost:5432/ecovision`
- `CORS_ORIGINS`: e.g. `http://localhost:5173`
- `MAX_UPLOAD_MB`: e.g. `10`
- `MODEL_PATH`: e.g. `artifacts/model.pt`
- `CLASSES_PATH`: e.g. `artifacts/classes.json`
- `HIGH_THRESHOLD`: e.g. `0.80`
- `MODERATE_THRESHOLD`: e.g. `0.60`

## Local development

1. Activate environment: `.venv/bin/activate` (or source your virtual environment)
2. Start PostgreSQL locally (e.g. via Docker: `docker run --name ecovision-db -e POSTGRES_USER=ecovision -e POSTGRES_PASSWORD=ecovision -e POSTGRES_DB=ecovision -p 5432:5432 -d postgres:15`)
3. Run migrations: `alembic upgrade head`
4. Seed database: `python -m app.database.seed`
5. Start Uvicorn: `uvicorn app.main:app --reload`
6. Run tests: `pytest -q`

## Docker

Build the backend container:
```bash
docker build -t ecovision-backend:1.0 .
```

Run the backend container (requires PostgreSQL network):
```bash
docker run --rm \
  -p 8000:8000 \
  --network ecovision-net \
  -e DATABASE_URL=postgresql+psycopg://ecovision:password@ecovision-db:5432/ecovision \
  -e CORS_ORIGINS=http://localhost:5173 \
  ecovision-backend:1.0
```

## API

Final endpoints exposed:

- `GET /`
- `GET /health`
- `GET /api/categories`
- `GET /api/categories/{slug}`
- `GET /api/categories/{slug}/guidance`
- `POST /api/upload`
- `POST /api/classify`
- `GET /api/history`
- `GET /api/history/{id}`
- `GET /api/analytics/summary`
- `GET /api/analytics/categories`
- `GET /api/analytics/recent`

## Testing

Run the test suite with:
```bash
pytest -q
```

## Model

The PyTorch AI classification model and metadata must be placed in the `models/` directory:
- `models/best_model.pt`: The fine-tuned EfficientNet-B0 model checkpoint.
- `models/classes.json`: The class mapping which outputs exact waste slugs matching the DB.
- `models/model_metadata.json`: The model's validation metrics, config, and required normalization settings.

**Note**: The raw Kaggle dataset is not required at runtime. Only the trained artifact is needed. Inferences are executed efficiently on CPU or MPS/CUDA depending on availability.
