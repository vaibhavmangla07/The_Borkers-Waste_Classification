from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import categories, upload, classification

app = FastAPI(
    title=settings.APP_NAME,
    description="EcoVision AI — Smart Waste Classification & Disposal Intelligence Platform",
    version="0.1.0",
)

# Parse allowed origins from configuration
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(categories.router, prefix="")
app.include_router(upload.router, prefix="")
app.include_router(classification.router, prefix="")

@app.get("/")
def read_root():
    return {"message": "Welcome to EcoVision AI API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
