from fastapi import APIRouter
from app.api.v1.endpoints import classify, health, history

api_router = APIRouter()

api_router.include_router(health.router, tags=["System & Health"])
api_router.include_router(classify.router, prefix="/classify", tags=["Classification"])
api_router.include_router(history.router, prefix="/history", tags=["Scan History & Analytics"])
