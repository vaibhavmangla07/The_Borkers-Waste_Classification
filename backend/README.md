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
