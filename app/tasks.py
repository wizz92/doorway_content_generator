"""Background tasks for content generation."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from app.config import settings
from app.database import Job, SessionLocal
from app.repositories.job_repository import JobRepository
from app.services.content_generator import ContentGenerator
from app.services.file_storage import FileStorageService
from app.services.job_logger import JobLogger
from app.services.output_formatter import create_website_file
from app.services.progress_tracker import ProgressTracker
from app.utils.logger import get_logger

logger = get_logger(__name__)


# Constants
CANCELLED_MESSAGE = "Cancelled by user"


def _is_job_cancelled(job_repository: JobRepository, job_id: str) -> bool:
    """
    Check if a job has been cancelled.
    
    Args:
        job_repository: JobRepository instance
        job_id: Job identifier
        
    Returns:
        True if job is cancelled, False otherwise
    """
    job = job_repository.get_by_id(job_id)
    if not job:
        return False
    return (
        job.status == "failed" and 
        job.error_message == CANCELLED_MESSAGE
    )


def _check_and_handle_cancellation(
    job_repository: JobRepository,
    job_id: str,
    context: str = ""
) -> bool:
    """
    Check if job is cancelled and log if so.
    
    Args:
        job_repository: JobRepository instance
        job_id: Job identifier
        context: Context message for logging
        
    Returns:
        True if job is cancelled, False otherwise
    """
    if _is_job_cancelled(job_repository, job_id):
        logger.info(f"Job {job_id} has been cancelled{', ' + context if context else ''}")
        return True
    return False


def _check_resume_status(job: Job) -> bool:
    """
    Check if job is being resumed from a previous checkpoint.
    
    Args:
        job: Job instance
        
    Returns:
        True if job is being resumed, False otherwise
    """
    return (
        job.status == "processing" or 
        (job.status == "failed" and job.keywords_completed and job.keywords_completed > 0)
    )


def _initialize_job(
    job: Job,
    keywords: List[str],
    num_websites: int,
    job_repository: JobRepository,
    job_logger: JobLogger
) -> Job:
    """
    Initialize job for processing.
    
    Args:
        job: Job instance
        keywords: List of keywords
        num_websites: Number of websites
        job_repository: JobRepository instance
        job_logger: JobLogger instance
        
    Returns:
        Updated job instance
    """
    job.status = "processing"
    job.total_keywords = len(keywords)
    job.completed_keywords = {}
    job = job_repository.update(job)
    job_logger.log_started(job.id, job.user_id or 0, len(keywords), num_websites)
    return job


def _ensure_completed_keywords_dict(job: Job) -> Dict[str, List[str]]:
    """
    Ensure completed_keywords is a proper dictionary structure.
    
    Args:
        job: Job instance
        
    Returns:
        Normalized completed_keywords dictionary
    """
    if job.completed_keywords is None:
        job.completed_keywords = {}
    elif not isinstance(job.completed_keywords, dict):
        job.completed_keywords = {}
    return job.completed_keywords


def _get_completed_keywords_for_website(
    file_storage: FileStorageService,
    job_id: str,
    website_index: int,
    keywords: List[str]
) -> List[str]:
    """
    Get list of keywords already completed for a website.
    
    Args:
        file_storage: FileStorageService instance
        job_id: Job identifier
        website_index: Website index (1-based)
        keywords: List of all keywords
        
    Returns:
        List of completed keywords
    """
    return file_storage.get_completed_keywords(job_id, website_index, keywords)


def _mark_keyword_completed(
    job: Job,
    website_index: int,
    keyword: str,
    job_repository: JobRepository
) -> None:
    """
    Mark a keyword as completed for a website.
    
    Args:
        job: Job instance
        website_index: Website index (1-based)
        keyword: Keyword to mark as completed
        job_repository: JobRepository instance
    """
    _ensure_completed_keywords_dict(job)
    website_key = str(website_index)
    
    if website_key not in job.completed_keywords:
        job.completed_keywords[website_key] = []
    elif not isinstance(job.completed_keywords[website_key], list):
        job.completed_keywords[website_key] = []
    
    if keyword not in job.completed_keywords[website_key]:
        job.completed_keywords[website_key].append(keyword)


def _load_existing_keyword_content(
    file_storage: FileStorageService,
    job_id: str,
    website_index: int,
    completed_keywords: List[str]
) -> Dict[str, str]:
    """
    Load existing content for completed keywords.
    
    Args:
        file_storage: FileStorageService instance
        job_id: Job identifier
        website_index: Website index (1-based)
        completed_keywords: List of completed keywords
        
    Returns:
        Dictionary mapping keyword to content
    """
    keyword_content_map = {}
    for keyword in completed_keywords:
        existing_content = file_storage.load_keyword_content(job_id, website_index, keyword)
        if existing_content:
            keyword_content_map[keyword] = existing_content
            logger.debug(f"Loaded existing content for keyword '{keyword}' in website {website_index}")
    return keyword_content_map


def _process_single_keyword(
    job_id: str,
    keyword: str,
    website_index: int,
    lang: str,
    geo: str,
    generator: ContentGenerator,
    file_storage: FileStorageService
) -> Tuple[str, str, bool]:
    """
    Process a single keyword: generate content and save to file.
    This function is designed to run in a worker thread.
    
    Args:
        job_id: Job identifier
        keyword: Keyword to process
        website_index: Website index (1-based)
        lang: Language code
        geo: Geography code
        generator: ContentGenerator instance
        file_storage: FileStorageService instance
        
    Returns:
        Tuple of (keyword, content, success) where:
        - keyword: The processed keyword
        - content: Generated content or error message
        - success: True if generation succeeded, False otherwise
    """
    try:
        # Generate content
        content = generator.generate_content_for_keyword(
            keyword=keyword,
            lang=lang,
            geo=geo,
            website_index=website_index
        )
        
        # Save immediately (checkpoint)
        file_storage.save_keyword_content(
            job_id=job_id,
            website_index=website_index,
            keyword=keyword,
            lang=lang,
            geo=geo,
            content=content
        )
        
        logger.debug(f"Successfully processed keyword '{keyword}' for website {website_index}")
        return (keyword, content, True)
        
    except Exception as e:
        error_msg = f"Error generating content for keyword '{keyword}': {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # Save error placeholder
        error_content = f"<p>Error: {str(e)}</p>"
        try:
            file_storage.save_keyword_content(
                job_id=job_id,
                website_index=website_index,
                keyword=keyword,
                lang=lang,
                geo=geo,
                content=error_content
            )
        except Exception as save_error:
            logger.error(f"Failed to save error content for keyword '{keyword}': {save_error}", exc_info=True)
        
        return (keyword, error_content, False)


def _process_remaining_keywords(
    job_id: str,
    remaining_keywords: List[str],
    website_index: int,
    lang: str,
    geo: str,
    generator: ContentGenerator,
    file_storage: FileStorageService,
    job_repository: JobRepository,
    progress_tracker: ProgressTracker,
    max_workers: int,
    total_tasks: int,
    keyword_content_map: Dict[str, str]
) -> Tuple[int, Dict[str, str]]:
    """
    Process remaining keywords in parallel.
    
    Args:
        job_id: Job identifier
        remaining_keywords: List of keywords to process
        website_index: Website index (1-based)
        lang: Language code
        geo: Geography code
        generator: ContentGenerator instance
        file_storage: FileStorageService instance
        job_repository: JobRepository instance
        progress_tracker: ProgressTracker instance
        max_workers: Maximum number of parallel workers
        total_tasks: Total number of tasks
        keyword_content_map: Dictionary to update with results
        
    Returns:
        Tuple of (completed_tasks_count, updated_keyword_content_map)
    """
    completed_count = 0
    
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_keyword = {
                    executor.submit(
                        _process_single_keyword,
                        job_id,
                        keyword,
                        website_index,
                        lang,
                        geo,
                        generator,
                        file_storage
                    ): keyword
                    for keyword in remaining_keywords
                }
                
                for future in as_completed(future_to_keyword):
            if _check_and_handle_cancellation(job_repository, job_id, "stopping keyword processing"):
                _cancel_pending_futures(future_to_keyword)
                break
                    
                    keyword = future_to_keyword[future]
                    if future.cancelled():
                        logger.debug(f"Future for keyword '{keyword}' was cancelled, skipping")
                        continue
                    
                    try:
                        processed_keyword, content, success = future.result()
                        keyword_content_map[processed_keyword] = content
                completed_count += 1
                
                if _check_and_handle_cancellation(job_repository, job_id, f"stopping after keyword '{processed_keyword}'"):
                    _cancel_pending_futures(future_to_keyword)
                    break
                
                # Update job state
                        job = job_repository.get_by_id(job_id)
                if job:
                    _mark_keyword_completed(job, website_index, processed_keyword, job_repository)
                    current_completed = job.keywords_completed or 0
                    job.keywords_completed = current_completed + 1
                    _ensure_completed_keywords_dict(job)
                    job_repository.update(job)
                    
                    # Update progress
                        progress_tracker.update_progress(
                            job_id=job_id,
                        completed_tasks=job.keywords_completed,
                            total_tasks=total_tasks,
                        keywords_completed=job.keywords_completed,
                            websites_completed=website_index - 1
                        )
                        
                        status_text = "successfully" if success else "with errors"
                logger.debug(f"Completed keyword '{processed_keyword}' for website {website_index} {status_text}")
                        
                    except Exception as e:
                        logger.error(f"Unexpected error processing keyword '{keyword}': {e}", exc_info=True)
                completed_count += 1
                        error_content = f"<p>Error: {str(e)}</p>"
                        keyword_content_map[keyword] = error_content
                
                        try:
                            file_storage.save_keyword_content(
                                job_id=job_id,
                                website_index=website_index,
                                keyword=keyword,
                                lang=lang,
                                geo=geo,
                                content=error_content
                            )
                        except Exception as save_error:
                            logger.error(f"Failed to save error content for keyword '{keyword}': {save_error}", exc_info=True)
                        
                        # Update job state for failed keyword
                        job = job_repository.get_by_id(job_id)
                        if job:
                    _mark_keyword_completed(job, website_index, keyword, job_repository)
                            job_repository.update(job)
            
    return completed_count, keyword_content_map


def _cancel_pending_futures(future_to_keyword: Dict) -> None:
    """
    Cancel all pending futures.
    
    Args:
        future_to_keyword: Dictionary mapping futures to keywords
    """
    cancelled_count = 0
    for pending_future in future_to_keyword:
        if not pending_future.done():
            if pending_future.cancel():
                cancelled_count += 1
    logger.info(f"Cancelled {cancelled_count} pending keyword processing tasks")


def _process_website(
    job_id: str,
    website_index: int,
    keywords: List[str],
    lang: str,
    geo: str,
    generator: ContentGenerator,
    file_storage: FileStorageService,
    job_repository: JobRepository,
    progress_tracker: ProgressTracker,
    max_workers: int,
    total_tasks: int
) -> Tuple[Dict[str, str], str]:
    """
    Process a single website: generate content for all keywords.
    
    Args:
        job_id: Job identifier
        website_index: Website index (1-based)
        keywords: List of keywords
        lang: Language code
        geo: Geography code
        generator: ContentGenerator instance
        file_storage: FileStorageService instance
        job_repository: JobRepository instance
        progress_tracker: ProgressTracker instance
        max_workers: Maximum number of parallel workers
        total_tasks: Total number of tasks
        
    Returns:
        Tuple of (keyword_content_map, file_path)
    """
    # Get completed keywords for this website
    completed_for_website = _get_completed_keywords_for_website(
        file_storage, job_id, website_index, keywords
    )
    completed_keywords_set = set(completed_for_website)
    
    # Load existing content
    keyword_content_map = _load_existing_keyword_content(
        file_storage, job_id, website_index, completed_for_website
    )
    
    # Process remaining keywords
    remaining_keywords = [k for k in keywords if k not in completed_keywords_set]
    logger.info(
        f"Website {website_index}: {len(completed_for_website)} completed, "
        f"{len(remaining_keywords)} remaining (processing in parallel with {max_workers} workers)"
    )
    
    completed_count, keyword_content_map = _process_remaining_keywords(
        job_id=job_id,
        remaining_keywords=remaining_keywords,
        website_index=website_index,
        lang=lang,
        geo=geo,
        generator=generator,
        file_storage=file_storage,
        job_repository=job_repository,
        progress_tracker=progress_tracker,
        max_workers=max_workers,
        total_tasks=total_tasks,
        keyword_content_map=keyword_content_map
    )
    
    # Create and save website file
            file_content = create_website_file(
                website_index=website_index,
                lang=lang,
                geo=geo,
                keyword_content_map=keyword_content_map
            )
            
            file_path = file_storage.save_website_file(
                job_id=job_id,
                website_index=website_index,
                lang=lang,
                geo=geo,
                content=file_content
            )
    
    return keyword_content_map, file_path


def _finalize_website(
    job_id: str,
    website_index: int,
    file_path: str,
    website_file_paths: Dict[int, str],
    job_repository: JobRepository
) -> None:
    """
    Finalize a website: update job with website completion.
    
    Args:
        job_id: Job identifier
        website_index: Website index (1-based)
        file_path: Path to website file
        website_file_paths: Dictionary mapping website index to file path
        job_repository: JobRepository instance
    """
            website_file_paths[website_index] = file_path
            
            job = job_repository.get_by_id(job_id)
            if job:
                job.websites_completed = website_index
                job.output_files = website_file_paths
                job_repository.update(job)
        

def _finalize_job(
    job_id: str,
    num_websites: int,
    completed_tasks: int,
    website_file_paths: Dict[int, str],
    job_repository: JobRepository,
    job_logger: JobLogger
) -> None:
    """
    Mark job as completed.
    
    Args:
        job_id: Job identifier
        num_websites: Number of websites
        completed_tasks: Number of completed tasks
        website_file_paths: Dictionary mapping website index to file path
        job_repository: JobRepository instance
        job_logger: JobLogger instance
    """
        job = job_repository.get_by_id(job_id)
    if not job:
                return
            
            job.status = "completed"
            job.progress = 100
            job.websites_completed = num_websites
            job.keywords_completed = completed_tasks
            job.output_files = website_file_paths
            job.completed_at = datetime.utcnow()
    _ensure_completed_keywords_dict(job)
            job_repository.update(job)
            
            job_logger.log_completed(job_id, job.user_id or 0, num_websites, completed_tasks)
        

def _handle_job_failure(
    job: Optional[Job],
    job_id: str,
    error: Exception,
    job_repository: JobRepository,
    job_logger: JobLogger
) -> None:
    """
    Handle job failure, preserving progress if any.
    
    Args:
        job: Job instance (may be None)
        job_id: Job identifier
        error: Exception that caused failure
        job_repository: JobRepository instance
        job_logger: JobLogger instance
    """
    error_msg = f"Task failed for job {job_id}: {str(error)}"
        logger.error(error_msg, exc_info=True)
    
    if not job:
        return
    
            try:
                # Don't mark as failed if we made progress - allow resume
                if job.keywords_completed and job.keywords_completed > 0:
                    job.status = "processing"  # Keep as processing to allow resume
            logger.info(
                f"Job {job_id} failed but has progress ({job.keywords_completed} keywords). "
                "Can be resumed."
            )
                else:
                    job.status = "failed"
                
        job.error_message = str(error)
                job_repository.update(job)
        job_logger.log_failed(job_id, job.user_id or 0, str(error))
            except Exception as update_error:
                logger.error(f"Failed to update job status: {update_error}", exc_info=True)


def generate_content_task(
    job_id: str,
    keywords: List[str],
    lang: str,
    geo: str,
    num_websites: int,
    max_workers: Optional[int] = None
) -> None:
    """
    Background task to generate content for all keywords and websites.
    Now supports parallel keyword processing, incremental saving, and resume capability.
    
    Args:
        job_id: Job ID
        keywords: List of keywords
        lang: Language code
        geo: Geography code
        num_websites: Number of websites
        max_workers: Maximum number of parallel workers (defaults to settings.max_parallel_workers)
    """
    if max_workers is None:
        max_workers = settings.max_parallel_workers
    
    logger.info(
        f"Starting background task for job_id={job_id}, keywords_count={len(keywords)}, "
        f"lang={lang}, geo={geo}, num_websites={num_websites}, max_workers={max_workers}"
    )
    
    db = SessionLocal()
    job_repository = JobRepository(db)
    progress_tracker = ProgressTracker(db, job_repository)
    job_logger = JobLogger(db)
    generator = ContentGenerator()
    file_storage = FileStorageService()
    
    job = None
    
    try:
        job = job_repository.get_by_id(job_id)
        if not job:
            logger.error(f"Job {job_id} not found in database")
            return
        
        is_resume = _check_resume_status(job)
        if is_resume:
            logger.info(
                f"Resuming job {job_id} from previous checkpoint "
                f"(completed: {job.keywords_completed or 0} keywords)"
            )
        else:
            job = _initialize_job(job, keywords, num_websites, job_repository, job_logger)
        
        total_tasks = num_websites * len(keywords)
        completed_tasks = job.keywords_completed or 0
        website_file_paths = job.output_files or {}
        _ensure_completed_keywords_dict(job)
        
        # Process each website
        for website_index in range(1, num_websites + 1):
            if _check_and_handle_cancellation(job_repository, job_id, "stopping execution"):
                return
            
            job = job_repository.get_by_id(job_id)
            if not job:
                logger.error(f"Job {job_id} not found during processing")
                return
            
            _ensure_completed_keywords_dict(job)
            
            keyword_content_map, file_path = _process_website(
                job_id=job_id,
                website_index=website_index,
                keywords=keywords,
                lang=lang,
                geo=geo,
                generator=generator,
                file_storage=file_storage,
                job_repository=job_repository,
                progress_tracker=progress_tracker,
                max_workers=max_workers,
                total_tasks=total_tasks
            )
            
            if _check_and_handle_cancellation(job_repository, job_id, f"stopping before finalizing website {website_index}"):
                return
            
            _finalize_website(job_id, website_index, file_path, website_file_paths, job_repository)
            
            # Update completed tasks count
            job = job_repository.get_by_id(job_id)
            if job:
                completed_tasks = job.keywords_completed or 0
        
        if _check_and_handle_cancellation(job_repository, job_id, "not marking as completed"):
            return
        
        job = job_repository.get_by_id(job_id)
        if job and not _check_and_handle_cancellation(job_repository, job_id, "during final update"):
            _finalize_job(
                job_id, num_websites, completed_tasks, website_file_paths,
                job_repository, job_logger
            )
        
    except Exception as e:
        _handle_job_failure(job, job_id, e, job_repository, job_logger)
    finally:
        try:
            db.close()
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")

