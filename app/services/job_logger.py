"""Job logging service."""
import os
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.log import JobLog
from app.config import settings


class JobLogger:
    """Service for logging job events."""
    
    def __init__(self, db: Session):
        """
        Initialize job logger.
        
        Args:
            db: Database session
        """
        self.db = db
        self.enabled = settings.enable_job_logging
    
    def log(
        self,
        job_id: str,
        user_id: int,
        event_type: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a job event.
        
        Args:
            job_id: Job identifier
            user_id: User identifier
            event_type: Event type (created, started, progress, completed, failed)
            message: Log message
            metadata: Optional metadata dictionary
        """
        if not self.enabled:
            return
        
        try:
            job_log = JobLog(
                job_id=job_id,
                user_id=user_id,
                event_type=event_type,
                message=message,
                metadata_json=metadata or {}
            )
            self.db.add(job_log)
            self.db.commit()
        except Exception as e:
            print(f"Error logging job event: {e}")
            # Don't raise - logging failures shouldn't break the application
    
    def log_created(self, job_id: str, user_id: int, keywords_count: int) -> None:
        """Log job creation."""
        self.log(
            job_id=job_id,
            user_id=user_id,
            event_type="created",
            message=f"Job created with {keywords_count} keywords",
            metadata={"keywords_count": keywords_count}
        )
    
    def log_started(self, job_id: str, user_id: int, keywords_count: int, num_websites: int) -> None:
        """Log job start."""
        self.log(
            job_id=job_id,
            user_id=user_id,
            event_type="started",
            message=f"Job started processing {keywords_count} keywords for {num_websites} websites",
            metadata={"keywords_count": keywords_count, "num_websites": num_websites}
        )
    
    def log_completed(self, job_id: str, user_id: int, websites_completed: int, keywords_completed: int) -> None:
        """Log job completion."""
        self.log(
            job_id=job_id,
            user_id=user_id,
            event_type="completed",
            message=f"Job completed successfully. Generated {websites_completed} website files.",
            metadata={"websites_completed": websites_completed, "keywords_completed": keywords_completed}
        )
    
    def log_failed(self, job_id: str, user_id: int, error: str) -> None:
        """Log job failure."""
        self.log(
            job_id=job_id,
            user_id=user_id,
            event_type="failed",
            message=f"Job failed: {error}",
            metadata={"error": error}
        )

