"""Job service for business logic."""
import uuid
from typing import List, Dict
from sqlalchemy.orm import Session

from app.repositories.job_repository import JobRepository
from app.services.job_logger import JobLogger
from app.services.queue import QueueInterface
from app.services.output_formatter import create_zip_archive
from app.tasks import generate_content_task
from app.database import Job
from app.config import settings
from app.exceptions import JobNotFoundError, JobAccessDeniedError, JobInvalidStateError
from app.schemas import GenerateRequest, JobStatusResponse, JobResponse


class JobService:
    """Service for job business logic."""
    
    def __init__(
        self,
        db: Session,
        queue: QueueInterface,
        job_repository: JobRepository | None = None,
        job_logger: JobLogger | None = None
    ):
        """
        Initialize job service.
        
        Args:
            db: Database session
            queue: Queue service
            job_repository: Optional job repository (created if not provided)
            job_logger: Optional job logger (created if not provided)
        """
        self.db = db
        self.queue = queue
        self.job_repository = job_repository or JobRepository(db)
        self.job_logger = job_logger or JobLogger(db)
    
    def create_job(
        self,
        user_id: int,
        keywords: List[str]
    ) -> Job:
        """
        Create a new job.
        
        Args:
            user_id: User identifier
            keywords: List of keywords
            
        Returns:
            Created job instance
            
        Raises:
            ValueError: If keywords exceed maximum
        """
        if len(keywords) > settings.max_keywords:
            raise ValueError(f"Too many keywords. Maximum allowed: {settings.max_keywords}")
        
        job_id = str(uuid.uuid4())
        job = Job(
            id=job_id,
            user_id=user_id,
            status="queued",
            keywords=keywords,
            total_keywords=len(keywords)
        )
        
        job = self.job_repository.create(job)
        
        # Log job creation
        self.job_logger.log_created(job_id, user_id, len(keywords))
        
        return job
    
    def start_generation(
        self,
        request: GenerateRequest,
        user_id: int
    ) -> Dict:
        """
        Start content generation for a job.
        
        Args:
            request: Generation request
            user_id: User identifier
            
        Returns:
            Dictionary with status and job information
            
        Raises:
            JobNotFoundError: If job not found
            JobAccessDeniedError: If user doesn't own job
            ValueError: If parameters are invalid
        """
        # Get and validate job
        job = self.job_repository.get_and_validate_ownership(
            request.job_id,
            user_id
        )
        
        # Validate parameters
        if request.num_websites > settings.max_websites:
            raise ValueError(f"Too many websites. Maximum allowed: {settings.max_websites}")
        
        # Update job with parameters
        job.lang = request.lang
        job.geo = request.geo
        job.num_websites = request.num_websites
        job.status = "queued"
        job = self.job_repository.update(job)
        
        # Enqueue task
        self.queue.enqueue(
            generate_content_task,
            job_id=request.job_id,
            keywords=job.keywords,
            lang=request.lang,
            geo=request.geo,
            num_websites=request.num_websites,
            job_timeout=settings.task_timeout
        )
        
        # Estimate time (rough estimate: 5 seconds per keyword per website)
        estimated_time = len(job.keywords) * request.num_websites * 5
        
        return {
            "status": "queued",
            "estimated_time": estimated_time,
            "job_id": request.job_id,
            "using_redis": hasattr(self.queue, 'is_available') and self.queue.is_available()
        }
    
    def get_job_status(
        self,
        job_id: str,
        user_id: int
    ) -> JobStatusResponse:
        """
        Get job status.
        
        Args:
            job_id: Job identifier
            user_id: User identifier
            
        Returns:
            Job status response
            
        Raises:
            JobNotFoundError: If job not found
            JobAccessDeniedError: If user doesn't own job
        """
        job = self.job_repository.get_and_validate_ownership(job_id, user_id)
        job = self.job_repository.refresh_job(job)
        
        return JobStatusResponse(
            id=str(job.id),
            status=job.status or "queued",
            progress=job.progress or 0,
            keywords_completed=job.keywords_completed or 0,
            total_keywords=job.total_keywords or 0,
            websites_completed=job.websites_completed or 0,
            num_websites=job.num_websites or 0,
            error_message=job.error_message,
            created_at=job.created_at,
            completed_at=job.completed_at
        )
    
    def list_jobs(
        self,
        user_id: int,
        limit: int = 20
    ) -> List[JobResponse]:
        """
        List jobs for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of jobs to return
            
        Returns:
            List of job responses (NOT logs!)
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"🔍 JobService.list_jobs called: user_id={user_id}, limit={limit}")
        
        # Get jobs from repository (NOT logs!)
        jobs = self.job_repository.get_by_user(user_id, limit)
        logger.info(f"📊 Found {len(jobs)} jobs from JobRepository (NOT JobLog!)")
        
        if len(jobs) == 0:
            logger.warning(f"⚠️ No jobs found for user_id={user_id}")
            return []
        
        result = []
        for job in jobs:
            # CRITICAL: Verify this is a Job object, NOT a JobLog object
            if not isinstance(job, Job):
                logger.error(f"❌ CRITICAL ERROR: Expected Job object, got {type(job)}. This should never happen!")
                raise TypeError(f"Expected Job object, got {type(job)}. This indicates a bug in JobRepository.")
            
            # Verify this is a Job, not a JobLog (additional check)
            if not hasattr(job, 'id') or not hasattr(job, 'status'):
                logger.error(f"❌ Invalid job object: {type(job)}")
                continue
            
            # Ensure we have the required Job attributes (not JobLog attributes)
            if not hasattr(job, 'user_id') or not hasattr(job, 'created_at'):
                logger.error(f"❌ Job object missing required attributes: {type(job)}")
                continue
                
            # Refresh job to get latest updates
            try:
                job = self.job_repository.refresh_job(job)
            except Exception as e:
                logger.error(f"⚠️ Error refreshing job {job.id}: {e}")
                continue
            
            try:
                job_response = JobResponse.from_orm(job)
                # Verify the response is a JobResponse
                if not isinstance(job_response, JobResponse):
                    logger.error(f"❌ CRITICAL: JobResponse.from_orm returned {type(job_response)}, not JobResponse")
                    raise TypeError(f"Expected JobResponse, got {type(job_response)}")
                result.append(job_response)
                logger.debug(f"✅ Added job {job.id} (status={job.status}) to result")
            except Exception as e:
                logger.error(f"❌ Error converting job {job.id} to JobResponse: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        # Final verification: ensure we're returning a list of JobResponse
        if not isinstance(result, list):
            logger.error(f"❌ CRITICAL: Expected list, got {type(result)}")
            raise TypeError(f"Expected list of JobResponse, got {type(result)}")
        
        logger.info(f"📦 Returning {len(result)} JobResponse objects (NOT logs!) - verified type: {type(result[0]) if result else 'empty list'}")
        return result
    
    def cancel_job(
        self,
        job_id: str,
        user_id: int
    ) -> None:
        """
        Cancel a job.
        
        Args:
            job_id: Job identifier
            user_id: User identifier
            
        Raises:
            JobNotFoundError: If job not found
            JobAccessDeniedError: If user doesn't own job
            JobInvalidStateError: If job cannot be cancelled
        """
        job = self.job_repository.get_and_validate_ownership(job_id, user_id)
        
        if job.status not in ["queued", "processing"]:
            raise JobInvalidStateError(
                job_id=job_id,
                current_status=job.status,
                operation="cancel"
            )
        
        # Try to cancel in queue
        self.queue.cancel_job(job_id)
        
        # Update job status
        job.status = "failed"
        job.error_message = "Cancelled by user"
        self.job_repository.update(job)
    
    def download_results(
        self,
        job_id: str,
        user_id: int
    ) -> bytes:
        """
        Get download results for a completed job.
        
        Args:
            job_id: Job identifier
            user_id: User identifier
            
        Returns:
            ZIP file content as bytes
            
        Raises:
            JobNotFoundError: If job not found
            JobAccessDeniedError: If user doesn't own job
            JobInvalidStateError: If job is not completed
        """
        job = self.job_repository.get_and_validate_ownership(job_id, user_id)
        
        if job.status != "completed":
            raise JobInvalidStateError(
                job_id=job_id,
                current_status=job.status,
                operation="download"
            )
        
        if not job.output_files:
            raise ValueError(
                "Output files not found. Job may have been completed before file storage was implemented."
            )
        
        # Create ZIP archive
        return create_zip_archive(job.output_files, job.lang, job.geo)

