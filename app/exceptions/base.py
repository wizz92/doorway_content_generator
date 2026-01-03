"""Base exception classes."""
from fastapi import status


class AppException(Exception):
    """Base exception for application errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str | None = None
    ):
        """
        Initialize exception.
        
        Args:
            message: Error message
            status_code: HTTP status code
            detail: Additional error details
        """
        self.message = message
        self.status_code = status_code
        self.detail = detail or message
        super().__init__(self.message)

