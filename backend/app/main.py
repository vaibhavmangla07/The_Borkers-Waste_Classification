import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.routes import categories, upload, classification, history, analytics
from app.core.logging import setup_logging
from app.core.errors import AppError
from app.core.validators import RequestSizeLimitMiddleware

# 1. Setup Logging
setup_logging()
logger = logging.getLogger(__name__)

logger.info("Application starting up")

app = FastAPI(
    title=settings.APP_NAME,
    description="EcoVision AI — Smart Waste Classification & Disposal Intelligence Platform",
    version="0.1.0",
)

# 2. Middlewares
# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

# Size Limit Middleware
app.add_middleware(RequestSizeLimitMiddleware)

# CORS
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Exception Handlers
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request parameters"
            }
        }
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    code = "NOT_FOUND" if exc.status_code == 404 else "HTTP_ERROR"
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": str(exc.detail)
            }
        }
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "DATABASE_ERROR",
                "message": "Database operation failed"
            }
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal server error occurred"
            }
        }
    )

# 4. Routers
app.include_router(categories.router, prefix="")
app.include_router(upload.router, prefix="")
app.include_router(classification.router, prefix="")
app.include_router(history.router, prefix="")
app.include_router(analytics.router, prefix="")

@app.get("/")
def read_root():
    return {"message": "Welcome to EcoVision AI API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/readiness")
def readiness_check():
    from app.ai.model import ModelLoader
    return {
        "status": "ready",
        "model_available": ModelLoader.is_available()
    }
