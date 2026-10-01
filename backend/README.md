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

The AI classification model and metadata must be placed in the `artifacts/` directory:
- `artifacts/model.pt`: The PyTorch model checkpoint.
- `artifacts/classes.json`: The class mapping (must match the seeded categories in the DB).
- `artifacts/metrics.json`: Accuracy and other validation metrics.
