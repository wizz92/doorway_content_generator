"""Logging API endpoints."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_log_repository
from app.middleware.auth import get_current_user
from app.models.user import User
from app.repositories.log_repository import LogRepository
from app.utils.responses import success_response

router = APIRouter()


@router.get("")  # Changed from "/api" to "" since router has prefix "/api/logs"
async def get_api_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    endpoint: Optional[str] = None,
    method: Optional[str] = None,
    status_code: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    log_repository: LogRepository = Depends(get_log_repository)
):
    """
    Get API logs (only for authenticated users).
    
    Returns:
        Standardized response with API logs data
    """
    result = log_repository.get_api_logs(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        endpoint=endpoint,
        method=method,
        status_code=status_code
    )
    
    return success_response(data=result, message="API logs retrieved successfully")


@router.get("/jobs")  # This becomes /api/logs/jobs (NOT /api/jobs) due to router prefix
async def get_job_logs_disabled():
    """
    This endpoint is intentionally disabled to avoid confusion with /api/jobs.
    """
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Endpoint disabled"
    )

