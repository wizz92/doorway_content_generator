"""Job-related schemas."""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.database import Job


class GenerateRequest(BaseModel):
    """Request model for content generation."""
    job_id: str
    lang: str = Field(..., min_length=2, max_length=5, description="Language code (e.g., 'hu', 'en')")
    geo: str = Field(..., min_length=2, max_length=5, description="Geography code (e.g., 'HU', 'US')")
    num_websites: int = Field(..., ge=1, le=100, description="Number of websites (1-100)")


class JobStatusResponse(BaseModel):
    """Job status response model."""
    id: str
    status: str
    progress: int
    keywords_completed: int
    total_keywords: int
    websites_completed: int
    num_websites: int
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class JobResponse(BaseModel):
    """Job response model."""
    id: str
    status: str
    lang: str
    geo: str
    num_websites: int
    total_keywords: int
    keywords_completed: int
    websites_completed: int
    progress: int
    error_message: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
    
    @classmethod
    def from_orm(cls, job: Job) -> "JobResponse":
        """
        Create JobResponse from Job model.
        
        Args:
            job: Job model instance
            
        Returns:
            JobResponse instance
        """
        return cls(
            id=str(job.id),
            status=job.status or "queued",
            lang=job.lang or "",
            geo=job.geo or "",
            num_websites=job.num_websites or 0,
            total_keywords=job.total_keywords or 0,
            keywords_completed=job.keywords_completed or 0,
            websites_completed=job.websites_completed or 0,
            progress=job.progress or 0,
            error_message=job.error_message,
            created_at=format_datetime(job.created_at),
            completed_at=format_datetime(job.completed_at) if job.completed_at else None,
        )


class JobListResponse(BaseModel):
    """List of jobs response model."""
    jobs: List[JobResponse]


def format_datetime(dt: Optional[datetime]) -> str:
    """
    Format datetime to ISO string.
    
    Args:
        dt: Datetime object or None
        
    Returns:
        ISO formatted string or empty string if None
    """
    if dt is None:
        return ""
    if hasattr(dt, 'isoformat'):
        return dt.isoformat()
    return str(dt)

