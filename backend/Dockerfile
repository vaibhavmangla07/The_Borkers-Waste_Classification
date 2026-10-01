FROM python:3.11-slim

# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Install dependencies first (to leverage Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

# Copy application files
COPY alembic.ini .
COPY alembic/ ./alembic/
COPY app/ ./app/
COPY models/ ./models/
COPY scripts/ ./scripts/

# Ensure storage uploads directory exists and is writable
RUN mkdir -p storage/uploads && chown -R appuser:appuser storage
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

EXPOSE 8000

# Start Uvicorn directly
CMD uvicorn app.main:app --host 0.0.0.0 --port 8000
