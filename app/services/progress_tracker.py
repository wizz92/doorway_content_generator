"""Progress tracking service."""
from typing import Optional
from sqlalchemy.orm import Session

from app.database import Job
from app.repositories.job_repository import JobRepository


class ProgressTracker:
    """Service for tracking job progress."""
    
    def __init__(self, db: Session, job_repository: JobRepository | None = None):
        """
        Initialize progress tracker.
        
        Args:
            db: Database session
            job_repository: Optional job repository
        """
        self.db = db
        self.job_repository = job_repository or JobRepository(db)
    
    def update_progress(
        self,
        job_id: str,
        completed_tasks: int,
        total_tasks: int,
        keywords_completed: int | None = None,
        websites_completed: int | None = None
    ) -> None:
        """
        Update job progress.
        
        Args:
            job_id: Job identifier
            completed_tasks: Number of completed tasks
            total_tasks: Total number of tasks
            keywords_completed: Optional keywords completed count
            websites_completed: Optional websites completed count
        """
        job = self.job_repository.get_by_id(job_id)
        if not job:
            return
        
        progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
        
        job.progress = progress
        if keywords_completed is not None:
            job.keywords_completed = keywords_completed
        if websites_completed is not None:
            job.websites_completed = websites_completed
        
        self.job_repository.update(job)
        
        # Update RQ job metadata if available
        try:
            from rq import get_current_job
            rq_job = get_current_job()
            if rq_job:
                rq_job.meta['progress'] = progress
                rq_job.meta['keywords_completed'] = keywords_completed or completed_tasks
                rq_job.save_meta()
        except Exception:
            pass  # Ignore RQ errors if not using Redis

