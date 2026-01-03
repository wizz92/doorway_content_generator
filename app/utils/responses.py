"""Standardized API response utilities."""
from typing import Any, Dict, Optional


def success_response(data: Any, message: str = "Success") -> Dict[str, Any]:
    """
    Create a standardized success response.
    
    Args:
        data: Response data
        message: Success message
        
    Returns:
        Dictionary with standardized response format
    """
    return {
        "data": data,
        "error": None,
        "message": message
    }


def error_response(error: str, message: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a standardized error response.
    
    Args:
        error: Error detail
        message: Optional error message (defaults to error if not provided)
        
    Returns:
        Dictionary with standardized response format
    """
    return {
        "data": None,
        "error": error,
        "message": message or error
    }

