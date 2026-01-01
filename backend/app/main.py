"""
FastAPI application entry point.
Main application setup with routes, middleware, and configuration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root BEFORE importing settings
# In Docker, the project root is mounted at /workspace
# In local development, it's 3 levels up from backend/app/main.py
if Path("/workspace/.env").exists():
    # Docker environment
    load_dotenv(dotenv_path="/workspace/.env")
else:
    # Local development
    project_root = Path(__file__).parent.parent.parent
    load_dotenv(dotenv_path=project_root / ".env")

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import init_db
from app.db.qdrant import init_qdrant
from app.api.v1.endpoints import search, ingest


# Setup logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown."""
    # Startup
    print("🚀 Starting application...")
    
    # Initialize database
    try:
        init_db()
        print("✓ PostgreSQL initialized")
    except Exception as e:
        print(f"⚠️  PostgreSQL initialization failed: {e}")
    
    # Initialize Qdrant
    try:
        init_qdrant()
        print("✓ Qdrant initialized")
    except Exception as e:
        print(f"⚠️  Qdrant initialization failed: {e}")
    
    print("✓ Application startup complete\n")
    
    yield
    
    # Shutdown
    print("\n🛑 Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Semantic search API for apartment listings",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(search.router, prefix=settings.API_V1_PREFIX, tags=["search"])
app.include_router(ingest.router, prefix=settings.API_V1_PREFIX, tags=["ingest"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    from app.db.qdrant import qdrant_manager
    from sqlalchemy import text, create_engine
    from app.core.config import settings
    
    # Check Qdrant
    qdrant_healthy = qdrant_manager.health_check()
    
    # Check PostgreSQL (simple connection test)
    postgres_healthy = True
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        postgres_healthy = False
    
    status = "healthy" if (qdrant_healthy and postgres_healthy) else "unhealthy"
    
    return {
        "status": status,
        "qdrant": "healthy" if qdrant_healthy else "unhealthy",
        "postgresql": "healthy" if postgres_healthy else "unhealthy",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
