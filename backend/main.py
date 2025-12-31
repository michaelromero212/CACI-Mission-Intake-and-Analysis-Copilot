"""
CACI Mission Intake and Analysis Copilot - FastAPI Backend

A lightweight, AI-enabled accelerator for mission document analysis.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from config import get_settings
from db import init_db
from api import missions_router, analysis_router, reviews_router, analytics_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")


# Create FastAPI application
app = FastAPI(
    title="CACI Mission Intake and Analysis Copilot",
    description="""
    AI-enabled accelerator for mission document analysis.
    
    ## Features
    - **Document Ingestion**: Upload PDFs, CSVs, or submit free text
    - **AI Analysis**: Summarization, entity extraction, risk classification
    - **Cost Transparency**: Token usage and cost estimates for all AI operations
    - **Human-in-the-Loop**: Analyst review workflow support
    
    ## ESF-Aligned Design
    This is not a production system. It is an Enterprise Solutions Factory (ESF) 
    accelerator designed to demonstrate rapid time-to-value with AI-assisted analysis.
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(missions_router)
app.include_router(analysis_router)
app.include_router(reviews_router)
app.include_router(analytics_router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "CACI Mission Intake and Analysis Copilot",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "endpoints": {
            "missions": "/api/missions",
            "analysis": "/api/analysis",
            "reviews": "/api/reviews",
            "analytics": "/api/analytics"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "ai_model": settings.huggingface_model
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=True
    )
