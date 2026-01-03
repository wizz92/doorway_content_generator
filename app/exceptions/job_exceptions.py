"""Job-related exceptions."""
from fastapi import status
from app.exceptions.base import AppException


class JobNotFoundError(AppException):
    """Raised when a job is not found."""
    
    def __init__(self, job_id: str):
        """
        Initialize exception.
        
        Args:
            job_id: Job identifier that was not found
        """
        super().__init__(
            message=f"Job not found: {job_id}",
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
        self.job_id = job_id


class JobAccessDeniedError(AppException):
    """Raised when user doesn't have access to a job."""
    
    def __init__(self, job_id: str):
        """
        Initialize exception.
        
        Args:
            job_id: Job identifier that access was denied for
        """
        super().__init__(
            message=f"Access denied to job: {job_id}",
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
        self.job_id = job_id


class JobInvalidStateError(AppException):
    """Raised when a job operation is invalid for current state."""
    
    def __init__(self, job_id: str, current_status: str, operation: str):
        """
        Initialize exception.
        
        Args:
            job_id: Job identifier
            current_status: Current job status
            operation: Operation that was attempted
        """
        super().__init__(
            message=f"Cannot {operation} job {job_id} with status: {current_status}",
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot {operation} job with status: {current_status}"
        )
        self.job_id = job_id
        self.current_status = current_status
        self.operation = operation

