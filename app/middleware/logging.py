"""Logging middleware for API requests."""
import os
import asyncio
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal
from app.models.log import ApiLog
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all API requests."""
    
    async def dispatch(self, request: Request, call_next):
        # Skip logging for certain paths
        skip_paths = ["/docs", "/openapi.json", "/redoc", "/favicon.ico"]
        if any(request.url.path.startswith(path) for path in skip_paths):
            return await call_next(request)
        
        # Get user if authenticated (non-blocking)
        user_id = None
        try:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                # Run DB query in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                db = SessionLocal()
                try:
                    from app.models.session import Session as SessionModel
                    session = await loop.run_in_executor(
                        None,
                        lambda: db.query(SessionModel).filter(SessionModel.token == token).first()
                    )
                    if session and not session.is_expired():
                        user_id = session.user_id
                finally:
                    db.close()
        except Exception:
            pass
        
        # Process request
        response = await call_next(request)
        
        # Log to database asynchronously (don't block response)
        if os.getenv("ENABLE_API_LOGGING", "true").lower() == "true":
            # Log in background to avoid blocking
            asyncio.create_task(self._log_request_async(user_id, request, response))
        
        return response
    
    async def _log_request_async(self, user_id, request: Request, response):
        """Log request asynchronously."""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._log_request_sync(user_id, request, response)
            )
        except Exception as e:
            logger.error(f"Error logging API request: {e}", exc_info=True)
    
    def _log_request_sync(self, user_id, request: Request, response):
        """Synchronous logging function."""
        db = SessionLocal()
        try:
            api_log = ApiLog(
                user_id=user_id,
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code,
                request_data=None,  # Don't log request body to avoid blocking
                response_data=None,  # Don't log response body to avoid blocking
                timestamp=datetime.utcnow()
            )
            db.add(api_log)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Error logging API request: {e}", exc_info=True)
        finally:
            db.close()
