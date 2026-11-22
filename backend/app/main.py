import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Ensure project root is in sys.path regardless of working directory
_ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR))
_BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.api.v1.router import api_router
from backend.app.database.session import init_db
from backend.app.ml.predictor import load_model_artifacts


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle manager."""
    print("Initializing Database tables...")
    await init_db()
    print("Preloading Machine Learning model artifacts in background...")
    async def preload():
        try:
            await asyncio.to_thread(load_model_artifacts)
            print("ML Models loaded successfully into memory.")
        except Exception as e:
            print(f"Warning: Could not preload ML models: {e}")
    asyncio.create_task(preload())
    yield
    print("Application shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Industry-Grade AI-Driven Transaction Risk Analysis and Financial Intelligence Platform",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENV
    }
