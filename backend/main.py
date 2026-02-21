"""FastAPI backend application entry point."""

import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Add project root to Python path to allow imports
# This ensures imports work when running: python backend/main.py
project_root = Path(__file__).parent.parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import config
from backend.api import health, relay

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format="[API] %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting AI Ticket Assistant Backend...")
    yield
    logger.info("Shutting down AI Ticket Assistant Backend...")


# Create FastAPI app
app = FastAPI(
    title="AI Ticket Assistant Backend",
    description="Backend API for AI-powered Discord ticket support bot",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS (allow all origins for MVP, restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)
app.include_router(relay.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "AI Ticket Assistant Backend",
        "version": "0.1.0",
        "status": "running",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host=config.host,
        port=config.port,
        reload=True,
        log_level=config.log_level.lower(),
    )

