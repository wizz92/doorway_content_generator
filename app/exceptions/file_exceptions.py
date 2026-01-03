"""File processing exceptions."""
from fastapi import status
from app.exceptions.base import AppException


class FileProcessingError(AppException):
    """Raised when file processing fails."""
    
    def __init__(self, message: str, detail: str | None = None):
        """
        Initialize exception.
        
        Args:
            message: Error message
            detail: Additional error details
        """
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or message
        )

