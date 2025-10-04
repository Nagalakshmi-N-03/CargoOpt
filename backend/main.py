import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import time

# Import the new API routes
from backend.api.routes import router as api_router
from backend.config.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting CargoOpt Backend Application...")
    
    # Create necessary directories
    os.makedirs("exports", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        # Don't raise to allow app to start without database
    
    logger.info("CargoOpt Backend started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down CargoOpt Backend...")

app = FastAPI(
    title="Cargo Space Optimization API",
    description="Advanced API for optimizing cargo space usage in shipping containers using multiple algorithms",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the new API routes
app.include_router(api_router)

# Global exception handlers
@app.exception_handler(500)
async def internal_server_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": time.time()
        }
    )

@app.exception_handler(422)
async def validation_error_handler(request, exc):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation error",
            "message": "Invalid request parameters",
            "timestamp": time.time()
        }
    )

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error": "Not found",
            "message": "The requested resource was not found",
            "timestamp": time.time()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": time.time()
        }
    )

@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Cargo Space Optimization API",
        "version": "3.0.0",
        "description": "Advanced cargo space optimization using multiple algorithms",
        "endpoints": {
            "documentation": "/docs",
            "health": "/api/v1/health",
            "algorithms": "/api/v1/algorithms",
            "optimization": {
                "auto": "/api/v1/optimize/auto",
                "packing": "/api/v1/optimize/packing",
                "genetic": "/api/v1/optimize/genetic",
                "stowage": "/api/v1/optimize/stowage",
                "compare": "/api/v1/optimize/compare",
                "batch": "/api/v1/optimize/batch"
            },
            "validation": {
                "data": "/api/v1/validate/data",
                "placement": "/api/v1/validate/placement"
            },
            "utilities": {
                "container_types": "/api/v1/containers/types",
                "history": "/api/v1/optimize/history",
                "export": "/api/v1/export/result"
            }
        },
        "features": [
            "Multiple optimization algorithms",
            "3D container packing",
            "Genetic algorithm optimization",
            "Multi-container stowage",
            "Batch processing",
            "Real-time validation",
            "Comprehensive reporting",
            "RESTful API"
        ]
    }

@app.get("/health", include_in_schema=False)
async def health():
    """Simple health check"""
    return {
        "status": "healthy",
        "service": "CargoOpt API",
        "timestamp": time.time()
    }

# Add startup and shutdown events for better control
@app.on_event("startup")
async def startup_event():
    """Additional startup tasks"""
    logger.info("CargoOpt API is starting up...")
    
    # Initialize additional services if needed
    try:
        # Pre-load any necessary data or caches
        logger.info("Pre-loading completed")
    except Exception as e:
        logger.warning(f"Pre-loading failed: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup tasks on shutdown"""
    logger.info("CargoOpt API is shutting down...")
    
    # Cleanup tasks
    try:
        # Close database connections, cleanup temp files, etc.
        logger.info("Cleanup completed")
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment variables with defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    logger.info(f"Starting server on {host}:{port} (reload: {reload})")
    
    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
        access_log=True
    )