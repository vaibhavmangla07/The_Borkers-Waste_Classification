from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app import __version__
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    logger.info(f"Starting {settings.PROJECT_NAME} v{__version__} [{settings.ENVIRONMENT}]")
    
    # Ensure upload directory exists
    upload_dir = settings.upload_dir_path
    logger.info(f"Upload directory initialized at: {upload_dir}")
    
    # Initialize DB tables
    await init_db()
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Production-grade backend service for Waste Classification. "
        "Supports real-time image inference, batch scanning, multi-category recycling guidance, "
        "and scan history analytics."
    ),
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploaded image previews
app.mount("/static/uploads", StaticFiles(directory=str(settings.upload_dir_path)), name="uploads")

# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", summary="Root Index", include_in_schema=False)
async def root():
    return JSONResponse(
        content={
            "app": settings.PROJECT_NAME,
            "version": __version__,
            "status": "online",
            "documentation": "/docs",
            "redoc": "/redoc",
            "health_check": f"{settings.API_V1_STR}/health",
            "categories": f"{settings.API_V1_STR}/classify/categories"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
