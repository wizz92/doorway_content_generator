"""Main FastAPI application."""
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes import router
from app.api.auth import router as auth_router
from app.api.logs import router as logs_router
from app.middleware.logging import LoggingMiddleware
from app.config import settings
from app.exceptions import AppException
from app.exceptions.handlers import (
    app_exception_handler,
    validation_exception_handler,
    database_exception_handler,
    generic_exception_handler,
)

app = FastAPI(
    title="Multi-Website Content Generator",
    description="Generate content variations for multiple websites",
    version="1.0.0"
)

# CORS middleware - use settings from config
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add logging middleware
if settings.enable_api_logging:
    app.add_middleware(LoggingMiddleware)

# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include API routes
# Order matters - more specific routes first
# IMPORTANT: Register main routes FIRST to ensure /api/jobs is matched before logs router
# The main router has routes with /api prefix hardcoded (e.g., /api/jobs)
app.include_router(router, tags=["main"])  # Main routes include /api/jobs - NO prefix, routes already have /api prefix
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
# Logs router has prefix /api/logs, so /jobs route becomes /api/logs/jobs (NOT /api/jobs)
# app.include_router(logs_router, prefix="/api/logs", tags=["logs"])  # Logs routes under /api/logs (not /api/jobs)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    import logging
    from app.database import init_db
    
    logger = logging.getLogger(__name__)
    logger.info("Initializing database...")
    init_db()
    
    # Log registered routes for debugging
    logger.info("Registered routes:")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = ', '.join(route.methods) if route.methods else 'N/A'
            logger.info(f"  {methods:10} {route.path}")


# Serve React frontend in production
if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    from app.config import settings
    uvicorn.run(app, host="0.0.0.0", port=settings.backend_port)

