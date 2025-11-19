"""
SaferCall AI Backend - Main Application Entry Point
Real-time scam detection powered by AI and ML
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import logging.config
import os
from contextlib import asynccontextmanager
from app.routes import router
from app.config import get_settings, LOGGING_CONFIG

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting SaferCall AI Backend...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug Mode: {settings.debug_mode}")
    yield
    logger.info("Shutting down SaferCall AI Backend...")

app = FastAPI(
    title="SaferCall AI Backend",
    description="Real-time scam detection API powered by AI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
allowed_origins = settings.allowed_origins.split(",") if settings.allowed_origins != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation error",
            "details": exc.errors()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error",
            "message": str(exc) if settings.debug_mode else "An error occurred"
        }
    )

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "SaferCall AI API is running",
        "version": "1.0.0",
        "environment": settings.environment,
        "docs": "/docs",
        "health": "/health"
    }

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["Scam Detection"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug_mode,
        log_level=settings.log_level.lower()
    )
