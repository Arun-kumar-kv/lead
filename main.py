"""
FastAPI Main Application - TERP Leads Analytics Dashboard
Matches your exact project structure: app/api/leads_dashboard/dashboard.py
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import time
from typing import Dict, Any
from sqlalchemy import text
# Import database - matching your structure
from app.services.database import engine, get_db

# Import API router - matching YOUR exact structure
# from app.api.leads_dashboard import dashboard
from app.api.v1.api import api_router
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# APPLICATION LIFECYCLE
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - runs on startup and shutdown"""
    # Startup
    logger.info("🚀 Starting TERP Leads Analytics API")
    
    # Test database connection
    try:
        with engine.connect() as conn:
            logger.info("✅ Database connection successful")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down TERP Leads Analytics API")
    engine.dispose()

# ============================================================================
# CREATE APPLICATION
# ============================================================================

app = FastAPI(
    title="TERP Leads Analytics API",
    description="Hybrid analytics dashboard for TERP leads management system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# ============================================================================
# MIDDLEWARE
# ============================================================================

# CORS Middleware - Allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add X-Process-Time header to track response time"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.3f}"
    return response

# Logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    logger.info(f"→ {request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"← {request.method} {request.url.path} - {response.status_code}")
    return response

# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed information"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "message": "Validation error"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions gracefully"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": str(exc)
        }
    )

# ============================================================================
# INCLUDE ROUTERS
# ============================================================================

# Include your dashboard router - matching your structure
# app.include_router(
#     dashboard.router,
#     prefix="/api/leads-dashboard",
#     tags=["Leads Dashboard"]
# )
app.include_router(
    api_router,
    prefix="/api/v1"
)
# ============================================================================
# ROOT ENDPOINTS
# ============================================================================

@app.get("/", tags=["Root"])
async def root() -> Dict[str, str]:
    """
    Root endpoint - API information
    """
    return {
        "name": "TERP Leads Analytics API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    db_status = "unhealthy"
    db_message = ""
    
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "healthy"
        db_message = "Database connection successful"
    except Exception as e:
        db_message = f"Database connection failed: {str(e)}"
        logger.error(db_message)
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": time.time(),
        "database": {
            "status": db_status,
            "message": db_message
        }
    }
# @app.get("/health", tags=["Health"])
# async def health_check() -> Dict[str, Any]:
#     """
#     Health check endpoint
#     Checks API status and database connectivity
#     """
#     db_status = "unhealthy"
#     db_message = ""
    
#     try:
#         with engine.connect() as conn:
#             conn.execute("SELECT 1")
#         db_status = "healthy"
#         db_message = "Database connection successful"
#     except Exception as e:
#         db_message = f"Database connection failed: {str(e)}"
#         logger.error(db_message)
    
#     return {
#         "status": "healthy" if db_status == "healthy" else "degraded",
#         "timestamp": time.time(),
#         "database": {
#             "status": db_status,
#             "message": db_message
#         }
#     }

@app.get("/api/info", tags=["Info"])
async def api_info() -> Dict[str, Any]:
    """
    API information and available endpoints
    """
    return {
        "title": "TERP Leads Analytics API",
        "version": "1.0.0",
        "description": "Hybrid analytics dashboard for TERP leads management",
        "endpoints": {
            "main_dashboard": "/api/leads-dashboard/",
            "live_queries": {
                "total_leads": "/api/leads-dashboard/live/total",
                "conversion_breakdown": "/api/leads-dashboard/live/conversion-breakdown",
                "ratings": "/api/leads-dashboard/live/ratings",
                "recent_leads": "/api/leads-dashboard/live/recent?limit=10"
            },
            "trends": {
                "conversion_trend": "/api/leads-dashboard/trends/conversion?days=30"
            }
        },
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        },
        "health_check": "/health"
    }

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("TERP Leads Analytics API")
    print("=" * 60)
    print("Starting server...")
    print("API Documentation: http://localhost:8000/docs")
    print("Alternative docs: http://localhost:8000/redoc")
    print("Health check: http://localhost:8000/health")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True,      # Auto-reload on code changes
        log_level="info"
    )