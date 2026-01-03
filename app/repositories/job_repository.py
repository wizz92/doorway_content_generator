"""Job repository for database access."""
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.database import Job


class JobRepository:
    """Repository for job data access operations."""
    
    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db
    
    def get_by_id(self, job_id: str) -> Optional[Job]:
        """
        Get job by ID.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job instance or None if not found
        """
        return self.db.query(Job).filter(Job.id == job_id).first()
    
    def get_by_user(self, user_id: int, limit: int = 20) -> List[Job]:
        """
        Get jobs for a specific user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of jobs to return
            
        Returns:
            List of jobs ordered by creation date (newest first)
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # IMPORTANT: Query Job table, NOT JobLog table!
        jobs = (
            self.db.query(Job)
            .filter(Job.user_id == user_id)
            .order_by(Job.created_at.desc())
            .limit(limit)
            .all()
        )
        
        logger.info(f"📋 JobRepository.get_by_user: Found {len(jobs)} Job objects (NOT JobLog!) for user_id={user_id}")
        
        # Verify we're returning Job objects, not JobLog objects
        for job in jobs:
            if not isinstance(job, Job):
                logger.error(f"❌ ERROR: Expected Job object, got {type(job)}")
            else:
                logger.debug(f"  ✓ Job {job.id}: status={job.status}, created_at={job.created_at}")
        
        return jobs
    
    def get_and_validate_ownership(
        self, 
        job_id: str, 
        user_id: int,
        raise_on_not_found: bool = True,
        raise_on_access_denied: bool = True
    ) -> Optional[Job]:
        """
        Get job by ID and validate user ownership.
        
        Args:
            job_id: Job identifier
            user_id: User identifier to validate ownership
            raise_on_not_found: If True, raise exception when job not found
            raise_on_access_denied: If True, raise exception when access denied
            
        Returns:
            Job instance if found and user owns it
            
        Raises:
            HTTPException: If job not found or user doesn't own it
        """
        job = self.get_by_id(job_id)
        
        if not job:
            if raise_on_not_found:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Job not found"
                )
            return None
        
        if job.user_id != user_id:
            if raise_on_access_denied:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
            return None
        
        return job
    
    def refresh_job(self, job: Job) -> Job:
        """
        Refresh job from database to get latest updates.
        
        Args:
            job: Job instance to refresh
            
        Returns:
            Refreshed job instance
        """
        try:
            self.db.refresh(job)
        except Exception:
            # If refresh fails, re-query the job
            refreshed_job = self.get_by_id(job.id)
            if not refreshed_job:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Job not found"
                )
            return refreshed_job
        return job
    
    def create(self, job: Job) -> Job:
        """
        Create a new job.
        
        Args:
            job: Job instance to create
            
        Returns:
            Created job instance
        """
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job
    
    def update(self, job: Job) -> Job:
        """
        Update an existing job.
        
        Args:
            job: Job instance to update
            
        Returns:
            Updated job instance
        """
        self.db.commit()
        self.db.refresh(job)
        return job
    
    def delete(self, job: Job) -> None:
        """
        Delete a job.
        
        Args:
            job: Job instance to delete
        """
        self.db.delete(job)
        self.db.commit()

