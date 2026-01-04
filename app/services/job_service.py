"""Job service for business logic."""
import uuid
from typing import Dict, List

from sqlalchemy.orm import Session

from app.config import settings
from app.constants import ESTIMATED_TIME_PER_KEYWORD_PER_WEBSITE_SECONDS
from app.database import Job
from app.exceptions import JobAccessDeniedError, JobInvalidStateError, JobNotFoundError
from app.repositories.job_repository import JobRepository
from app.schemas import GenerateRequest, JobResponse, JobStatusResponse
from app.services.file_storage import FileStorageService
from app.services.job_logger import JobLogger
from app.services.output_formatter import create_zip_archive
from app.services.queue import QueueInterface
from app.tasks import generate_content_task
from app.utils.logger import get_logger

logger = get_logger(__name__)


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
        self.file_storage = FileStorageService()
    
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
            max_workers=settings.max_parallel_workers,
            job_timeout=settings.task_timeout
        )
        
        # Estimate time (rough estimate: configured seconds per keyword per website)
        estimated_time = len(job.keywords) * request.num_websites * ESTIMATED_TIME_PER_KEYWORD_PER_WEBSITE_SECONDS
        
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
            List of job responses
        """
        jobs = self.job_repository.get_by_user(user_id, limit)
        
        if len(jobs) == 0:
            return []
        
        result = []
        for job in jobs:
            if not self._validate_job_object(job):
                continue
            
            refreshed_job = self._refresh_job_safely(job)
            if not refreshed_job:
                continue
            
            job_response = self._convert_job_to_response(refreshed_job)
            if job_response:
                result.append(job_response)
        
        logger.debug(f"Returning {len(result)} jobs for user {user_id}")
        return result
    
    def _validate_job_object(self, job: Job) -> bool:
        """
        Validate that job object has required attributes.
        
        Args:
            job: Job object to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(job, Job):
            logger.error(f"Expected Job object, got {type(job)}")
            return False
        
        if not hasattr(job, 'id') or not hasattr(job, 'status'):
            logger.warning(f"Invalid job object: {type(job)}")
            return False
        
        return True
    
    def _refresh_job_safely(self, job: Job) -> Job | None:
        """
        Refresh job from database safely, handling errors.
        
        Args:
            job: Job object to refresh
            
        Returns:
            Refreshed job or None if refresh fails
        """
        try:
            return self.job_repository.refresh_job(job)
        except Exception as e:
            logger.error(f"Error refreshing job {job.id}: {e}", exc_info=True)
            return None
    
    def _convert_job_to_response(self, job: Job) -> JobResponse | None:
        """
        Convert job to JobResponse safely, handling errors.
        
        Args:
            job: Job object to convert
            
        Returns:
            JobResponse or None if conversion fails
        """
        try:
            job_response = JobResponse.from_orm(job)
            if not isinstance(job_response, JobResponse):
                logger.error(f"JobResponse.from_orm returned {type(job_response)}")
                return None
            return job_response
        except Exception as e:
            logger.error(f"Error converting job {job.id} to JobResponse: {e}", exc_info=True)
            return None
    
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
    
    def resume_job(
        self,
        job_id: str,
        user_id: int
    ) -> Dict:
        """
        Resume a failed or interrupted job from the last checkpoint.
        
        Args:
            job_id: Job identifier
            user_id: User identifier
            
        Returns:
            Dictionary with status and job information
            
        Raises:
            JobNotFoundError: If job not found
            JobAccessDeniedError: If user doesn't own job
            ValueError: If job cannot be resumed
        """
        from app.constants import ESTIMATED_TIME_PER_KEYWORD_PER_WEBSITE_SECONDS
        
        job = self.job_repository.get_and_validate_ownership(job_id, user_id)
        
        # Check if job can be resumed
        if job.status == "completed":
            raise ValueError("Job is already completed")
        
        if job.status not in ["processing", "failed"]:
            raise ValueError(f"Job cannot be resumed from status: {job.status}")
        
        if not job.keywords or not job.lang or not job.geo or not job.num_websites:
            raise ValueError("Job is missing required parameters for resumption")
        
        # Check if there's any progress to resume from
        if not job.keywords_completed or job.keywords_completed == 0:
            logger.warning(f"Job {job_id} has no progress to resume from. Starting fresh.")
        
        # Update job status to queued for processing
        job.status = "queued"
        job.error_message = None
        job = self.job_repository.update(job)
        
        # Enqueue task with existing parameters
        self.queue.enqueue(
            generate_content_task,
            job_id=job_id,
            keywords=job.keywords,
            lang=job.lang,
            geo=job.geo,
            num_websites=job.num_websites,
            job_timeout=settings.task_timeout
        )
        
        # Calculate remaining work
        total_keywords = len(job.keywords)
        completed_keywords = job.keywords_completed or 0
        remaining_keywords = total_keywords - completed_keywords
        
        estimated_time = remaining_keywords * job.num_websites * ESTIMATED_TIME_PER_KEYWORD_PER_WEBSITE_SECONDS
        
        logger.info(f"Resuming job {job_id}: {completed_keywords}/{total_keywords} keywords completed")
        
        return {
            "status": "queued",
            "estimated_time": estimated_time,
            "job_id": job_id,
            "resumed": True,
            "previous_progress": completed_keywords,
            "total_keywords": total_keywords,
            "remaining_keywords": remaining_keywords
        }
    
    def _read_website_files(self, job_id: str, job) -> Dict[int, str]:
        """
        Read website files from filesystem or legacy format.
        
        Args:
            job_id: Job identifier
            job: Job instance
            
        Returns:
            Dictionary mapping website index to file content
            
        Raises:
            ValueError: If files cannot be read
        """
        try:
            return self.file_storage.get_all_website_files(
                job_id=job_id,
                lang=job.lang,
                geo=job.geo
            )
        except Exception as e:
            # Fallback: check for legacy format
            if job.output_files and isinstance(job.output_files, dict):
                first_value = next(iter(job.output_files.values()), None)
                if first_value and isinstance(first_value, str) and len(first_value) > 100:
                    return job.output_files
            raise ValueError(
                f"Output files not found for job {job_id}: {str(e)}"
            )
    
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
        
        website_files = self._read_website_files(job_id, job)
        
        if not website_files:
            raise ValueError(f"No output files found for job {job_id}")
        
        return create_zip_archive(website_files, job.lang, job.geo)

