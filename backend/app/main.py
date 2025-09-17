"""
FastAPI Main Application for PPV System Health Monitor

This is the orchestration layer that coordinates:
- Phase 1: Database Models (Campaign, UploadSession)
- Phase 2: Core Services (DataConverter, RuntimeParser, CampaignClassifier)
- Phase 3: API Endpoints (XLSX Upload, Campaign Retrieval, Analytics)

Educational Focus: Shows how to structure a production-ready FastAPI application
with proper dependency injection, error handling, and business logic integration.

Key Architecture Decisions:
1. Service Layer Pattern: Controllers delegate to services for business logic
2. Dependency Injection: Database sessions and services injected via FastAPI
3. Fulfillment Focus: All endpoints emphasize impression delivery calculations
4. Error Handling: Consistent error responses with business context
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import uvicorn
from typing import Dict, Any

# Import our database and models
from .database import init_db, close_db, check_database_connection
from .models.campaign import Campaign, UploadSession

# Import API routers
from .api.upload import router as upload_router
from .api.campaigns import router as campaigns_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.

    Handles:
    - Database initialization on startup
    - Connection health checks
    - Clean shutdown procedures
    """
    # Startup
    logger.info("Starting PPV System Health Monitor API...")

    try:
        # Skip database initialization during testing
        import os
        if os.getenv("TESTING") != "1":
            # Initialize database
            init_db()
            logger.info("Database initialized successfully")

            # Verify database connection
            if not check_database_connection():
                raise ConnectionError("Database connection failed during startup")

        logger.info("API startup completed successfully")

    except Exception as e:
        logger.error(f"Startup failed: {e}")
        if os.getenv("TESTING") != "1":
            raise
        # In testing mode, continue without database connection
        logger.warning("Continuing in testing mode without database initialization")

    yield  # Application runs here

    # Shutdown
    logger.info("Shutting down PPV System Health Monitor API...")
    try:
        close_db()
        logger.info("API shutdown completed successfully")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")


# Create FastAPI application with fulfillment-focused title
app = FastAPI(
    title="PPV System Health Monitor - Campaign Fulfillment API",
    description="""
    **Campaign Data Foundation API** for XLSX processing and fulfillment analysis.

    ## Key Features:
    - **XLSX Upload Processing**: Coordinate DataConverter → RuntimeParser → CampaignClassifier → Database
    - **Fulfillment Analysis**: Calculate (delivered_impressions / impression_goal) * 100%
    - **Campaign vs Deal Classification**: Based on buyer field business rules
    - **Runtime Parsing**: Support ASAP and date range formats
    - **UUID Preservation**: Maintain data integrity from XLSX source

    ## Business Focus:
    This API prioritizes **campaign fulfillment tracking** over generic data management.
    All endpoints emphasize impression delivery calculations and completion status.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS configuration for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)


# Global exception handler for consistent error responses
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """
    Handle HTTP exceptions with consistent error response format.

    Provides business-context error messages focusing on fulfillment operations.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": str(request.url),
            "business_context": "Campaign Fulfillment Operations"
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """
    Handle unexpected exceptions with safe error responses.
    """
    logger.error(f"Unexpected error: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error during campaign processing",
            "status_code": 500,
            "timestamp": str(request.url),
            "business_context": "Campaign Fulfillment Operations"
        }
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for monitoring and deployment.

    Returns database connection status and application readiness.
    """
    db_healthy = check_database_connection()

    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "service": "PPV System Health Monitor API",
        "database": {
            "status": "connected" if db_healthy else "disconnected"
        },
        "features": {
            "xlsx_upload": "available",
            "fulfillment_analysis": "available",
            "campaign_classification": "available"
        }
    }


# Root endpoint with API information
@app.get("/", tags=["Info"])
async def root() -> Dict[str, Any]:
    """
    Root endpoint providing API overview and fulfillment focus.
    """
    return {
        "message": "PPV System Health Monitor - Campaign Fulfillment API",
        "version": "1.0.0",
        "purpose": "XLSX campaign processing with fulfillment analysis",
        "key_features": [
            "Campaign vs Deal classification",
            "Runtime parsing (ASAP and date ranges)",
            "Fulfillment percentage calculation",
            "UUID preservation from XLSX data"
        ],
        "endpoints": {
            "upload": "/api/v1/campaigns/upload",
            "campaigns": "/api/v1/campaigns/",
            "analytics": "/api/v1/campaigns/analytics/summary",
            "health": "/health",
            "docs": "/docs"
        }
    }


# Include API routers
app.include_router(upload_router, prefix="/api/v1", tags=["Upload"])
app.include_router(campaigns_router, prefix="/api/v1", tags=["Campaigns"])


if __name__ == "__main__":
    """
    Development server entry point.

    For production, use: uvicorn app.main:app --host 0.0.0.0 --port 8000
    """
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )