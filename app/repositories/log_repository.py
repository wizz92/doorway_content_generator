"""Log repository for database access."""
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.log import ApiLog, JobLog


class LogRepository:
    """Repository for log data access operations."""
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def get_api_logs(
        self,
        user_id: int,
        limit: int = 100,
        offset: int = 0,
        endpoint: Optional[str] = None,
        method: Optional[str] = None,
        status_code: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get API logs for a user with filtering and pagination.
        
        Args:
            user_id: User identifier
            limit: Maximum number of logs to return
            offset: Number of logs to skip
            endpoint: Optional endpoint filter
            method: Optional HTTP method filter
            status_code: Optional status code filter
            
        Returns:
            Dictionary with total, limit, offset, and logs list
        """
        query = self.db.query(ApiLog).filter(ApiLog.user_id == user_id)
        
        if endpoint:
            query = query.filter(ApiLog.endpoint.contains(endpoint))
        if method:
            query = query.filter(ApiLog.method == method)
        if status_code:
            query = query.filter(ApiLog.status_code == status_code)
        
        query = query.order_by(ApiLog.timestamp.desc())
        
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
    
    def get_job_logs(
        self,
        user_id: int,
        job_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get job logs for a user with optional job filter.
        
        Args:
            user_id: User identifier
            job_id: Optional job identifier filter
            limit: Maximum number of logs to return
            offset: Number of logs to skip
            
        Returns:
            Dictionary with total, limit, offset, and logs list
        """
        query = self.db.query(JobLog).filter(JobLog.user_id == user_id)
        
        if job_id:
            query = query.filter(JobLog.job_id == job_id)
        
        query = query.order_by(JobLog.timestamp.desc())
        
        total = query.count()
        logs = query.offset(offset).limit(limit).all()
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "logs": [
                {
                    "id": log.id,
                    "job_id": log.job_id,
                    "event_type": log.event_type,
                    "message": log.message,
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                    "metadata": log.metadata_json
                }
                for log in logs
            ]
        }

