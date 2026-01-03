"""Exception handlers for FastAPI."""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions.base import AppException


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Handle application exceptions.
    
    Args:
        request: FastAPI request
        exc: Application exception
        
    Returns:
        JSON error response
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "message": exc.message,
        }
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
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "message": "Validation error"
        }
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
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Database error occurred",
            "message": "An internal error occurred"
        }
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
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred",
            "message": str(exc)
        }
    )

