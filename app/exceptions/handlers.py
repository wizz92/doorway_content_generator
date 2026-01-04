"""Exception handlers for FastAPI."""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions.base import AppException
from app.exceptions.job_exceptions import (
    JobNotFoundError,
    JobAccessDeniedError,
    JobInvalidStateError,
)
from app.utils.logger import get_logger
from app.utils.responses import error_response

logger = get_logger(__name__)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Handle application exceptions.
    
    Args:
        request: FastAPI request
        exc: Application exception
        
    Returns:
        JSON error response
    """
    # Extract context from request
    user_id = getattr(request.state, 'user_id', None)
    job_id = getattr(request.state, 'job_id', None)
    
    # Log with context
    logger.error(
        f"Application exception: {exc.detail}",
        extra={
            "user_id": user_id,
            "job_id": job_id,
            "endpoint": request.url.path,
            "method": request.method,
            "status_code": exc.status_code
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(error=exc.detail, message=exc.message)
    )


async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle validation exceptions.
    
    Args:
        request: FastAPI request
        exc: Validation exception
        
    Returns:
        JSON error response
    """
    user_id = getattr(request.state, 'user_id', None)
    
    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={
            "user_id": user_id,
            "endpoint": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response(
            error="Validation error",
            message="Invalid request data"
        )
    )


async def database_exception_handler(
    request: Request,
    exc: SQLAlchemyError
) -> JSONResponse:
    """
    Handle database exceptions.
    
    Args:
        request: FastAPI request
        exc: Database exception
        
    Returns:
        JSON error response
    """
    user_id = getattr(request.state, 'user_id', None)
    job_id = getattr(request.state, 'job_id', None)
    
    # Log full error details server-side
    logger.error(
        f"Database error: {str(exc)}",
        extra={
            "user_id": user_id,
            "job_id": job_id,
            "endpoint": request.url.path,
            "method": request.method
        },
        exc_info=True
    )
    
    # Return sanitized error to client
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            error="Database error occurred",
            message="An internal error occurred"
        )
    )


async def job_not_found_handler(request: Request, exc: JobNotFoundError) -> JSONResponse:
    """
    Handle JobNotFoundError exceptions.
    
    Args:
        request: FastAPI request
        exc: JobNotFoundError exception
        
    Returns:
        JSON error response
    """
    user_id = getattr(request.state, 'user_id', None)
    
    logger.warning(
        f"Job not found: {exc.job_id}",
        extra={
            "user_id": user_id,
            "job_id": exc.job_id,
            "endpoint": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(error=exc.detail, message=exc.message)
    )


async def job_access_denied_handler(request: Request, exc: JobAccessDeniedError) -> JSONResponse:
    """
    Handle JobAccessDeniedError exceptions.
    
    Args:
        request: FastAPI request
        exc: JobAccessDeniedError exception
        
    Returns:
        JSON error response
    """
    user_id = getattr(request.state, 'user_id', None)
    
    logger.warning(
        f"Access denied to job: {exc.job_id}",
        extra={
            "user_id": user_id,
            "job_id": exc.job_id,
            "endpoint": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(error=exc.detail, message=exc.message)
    )


async def job_invalid_state_handler(request: Request, exc: JobInvalidStateError) -> JSONResponse:
    """
    Handle JobInvalidStateError exceptions.
    
    Args:
        request: FastAPI request
        exc: JobInvalidStateError exception
        
    Returns:
        JSON error response
    """
    user_id = getattr(request.state, 'user_id', None)
    
    logger.warning(
        f"Invalid job state: {exc.job_id}, status: {exc.current_status}, operation: {exc.operation}",
        extra={
            "user_id": user_id,
            "job_id": exc.job_id,
            "current_status": exc.current_status,
            "operation": exc.operation,
            "endpoint": request.url.path,
            "method": request.method
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(error=exc.detail, message=exc.message)
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle generic exceptions.
    
    Args:
        request: FastAPI request
        exc: Exception
        
    Returns:
        JSON error response
    """
    user_id = getattr(request.state, 'user_id', None)
    job_id = getattr(request.state, 'job_id', None)
    
    # Log full error details server-side
    logger.error(
        f"Unexpected error: {str(exc)}",
        extra={
            "user_id": user_id,
            "job_id": job_id,
            "endpoint": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__
        },
        exc_info=True
    )
    
    # Return sanitized error to client
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response(
            error="An unexpected error occurred",
            message="An internal error occurred"
        )
    )

