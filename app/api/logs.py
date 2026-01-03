"""Logging API endpoints."""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.log import ApiLog, JobLog
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("")  # Changed from "/api" to "" since router has prefix "/api/logs"
async def get_api_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    endpoint: Optional[str] = None,
    method: Optional[str] = None,
    status_code: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get API logs (only for authenticated users).
    """
    query = db.query(ApiLog)
    
    # Filter by current user (users can only see their own logs)
    query = query.filter(ApiLog.user_id == current_user.id)
    
    # Apply filters
    if endpoint:
        query = query.filter(ApiLog.endpoint.contains(endpoint))
    if method:
        query = query.filter(ApiLog.method == method)
    if status_code:
        query = query.filter(ApiLog.status_code == status_code)
    
    # Order by timestamp desc
    query = query.order_by(ApiLog.timestamp.desc())
    
    # Paginate
    total = query.count()
    logs = query.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "logs": [
            {
                "id": log.id,
                "endpoint": log.endpoint,
                "method": log.method,
                "status_code": log.status_code,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "request_data": log.request_data,
                "response_data": log.response_data
            }
            for log in logs
        ]
    }


@router.get("/jobs")  # This becomes /api/logs/jobs (NOT /api/jobs) due to router prefix
async def get_job_logs_disabled():
    """
    This endpoint is intentionally disabled to avoid confusion with /api/jobs.
    """
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Endpoint disabled"
    )

