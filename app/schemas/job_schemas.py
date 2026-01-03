"""Job-related schemas."""
from typing import List, Optional, Dict, Any
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
    keywords: Optional[List[str]] = None
    keyword_status: Optional[Dict[str, Dict[str, Any]]] = None
    
    @classmethod
    def from_orm(cls, job: Job) -> "JobResponse":
        """
        Create JobResponse from Job model.
        
        Args:
            job: Job model instance
            
        Returns:
            JobResponse instance
        """
        # Calculate keyword status
        keyword_status = cls._calculate_keyword_status(job)
        
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
            keywords=job.keywords if job.keywords else [],
            keyword_status=keyword_status,
        )
    
    @staticmethod
    def _calculate_keyword_status(job: Job) -> Dict[str, Dict[str, Any]]:
        """
        Calculate keyword completion status per website.
        
        Args:
            job: Job model instance
            
        Returns:
            Dictionary mapping keyword to status info:
            {
                "keyword1": {
                    "completed_websites": [1, 2],
                    "total_websites": 3
                },
                ...
            }
        """
        if not job.keywords or not isinstance(job.keywords, list):
            return {}
        
        num_websites = job.num_websites or 0
        
        # Normalize completed_keywords - handle JSON deserialization
        # SQLite may store JSON as TEXT, so we need to handle both dict and string
        import json
        completed_keywords = job.completed_keywords
        if completed_keywords is None:
            completed_keywords = {}
        elif isinstance(completed_keywords, str):
            # Try to parse JSON string
            try:
                parsed = json.loads(completed_keywords)
                completed_keywords = parsed if isinstance(parsed, dict) else {}
            except (json.JSONDecodeError, TypeError):
                completed_keywords = {}
        elif not isinstance(completed_keywords, dict):
            completed_keywords = {}
        
        # If job is completed but completed_keywords is empty, assume all keywords are completed for all websites
        # This handles legacy jobs created before checkpointing was implemented
        if job.status == "completed" and (not completed_keywords or len(completed_keywords) == 0):
            all_websites = list(range(1, num_websites + 1))
            return {keyword: {"completed_websites": all_websites, "total_websites": num_websites} for keyword in job.keywords}
        
        keyword_status = {}
        
        for keyword in job.keywords:
            completed_websites = []
            
            # Check each website index (1-based)
            for website_index in range(1, num_websites + 1):
                website_key = str(website_index)
                if website_key in completed_keywords:
                    completed_list = completed_keywords[website_key]
                    if isinstance(completed_list, list) and keyword in completed_list:
                        completed_websites.append(website_index)
            
            keyword_status[keyword] = {
                "completed_websites": completed_websites,
                "total_websites": num_websites
            }
        
        return keyword_status


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

