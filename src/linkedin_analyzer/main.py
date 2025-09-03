"""FastAPI application entry point for LinkedIn Company Analysis Tool."""

from datetime import datetime
from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from . import __version__
from .api.company_config import router as company_router
from .api.data_collection import router as data_router

# Create FastAPI application instance
app = FastAPI(
    title="LinkedIn Company Analysis Tool",
    description="A web-based demo application that analyzes LinkedIn posts for any user-specified company",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(company_router)
app.include_router(data_router)


@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handler for Pydantic validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "detail": exc.errors(),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for unhandled errors."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred. Please try again later.",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler for HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint to verify the service is running.

    Returns:
        Dict containing service status, version, and timestamp
    """
    return {
        "status": "healthy",
        "service": "LinkedIn Company Analysis Tool",
        "version": __version__,
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "development",
    }


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint providing basic API information.

    Returns:
        Dict with welcome message and API details
    """
    return {
        "message": "Welcome to LinkedIn Company Analysis Tool API",
        "version": __version__,
        "docs": "/docs",
        "health": "/health",
        "company_api": "/companies",
        "data_collection_api": "/data",
    }


if __name__ == "__main__":
    # Run the application with uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
