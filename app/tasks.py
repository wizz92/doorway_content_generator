"""Background tasks for content generation."""
from typing import List, Dict, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.database import SessionLocal
from app.repositories.job_repository import JobRepository
from app.services.content_generator import ContentGenerator
from app.services.output_formatter import create_website_file
from app.services.progress_tracker import ProgressTracker
from app.services.job_logger import JobLogger
from app.services.file_storage import FileStorageService
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


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
        job.error_message == "Cancelled by user"
    )


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


def generate_content_task(
    job_id: str,
    keywords: List[str],
    lang: str,
    geo: str,
    num_websites: int,
    max_workers: int = None
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
    # Use provided max_workers or default from settings
    if max_workers is None:
        max_workers = settings.max_parallel_workers
    
    logger.info(f"Starting background task for job_id={job_id}, keywords_count={len(keywords)}, lang={lang}, geo={geo}, num_websites={num_websites}, max_workers={max_workers}")
    
    db = SessionLocal()
    job_repository = JobRepository(db)
    progress_tracker = ProgressTracker(db, job_repository)
    job_logger = JobLogger(db)
    generator = ContentGenerator()
    file_storage = FileStorageService()
    
    job = None
    
    try:
        # Get job and update status
        job = job_repository.get_by_id(job_id)
        if not job:
            logger.error(f"Job {job_id} not found in database")
            return
        
        # Check if this is a resume (job was previously processing)
        is_resume = job.status == "processing" or (job.status == "failed" and job.keywords_completed and job.keywords_completed > 0)
        
        if is_resume:
            logger.info(f"Resuming job {job_id} from previous checkpoint (completed: {job.keywords_completed or 0} keywords)")
        else:
            job.status = "processing"
            job.total_keywords = len(keywords)
            job.completed_keywords = {}  # Initialize tracking
            job = job_repository.update(job)
            job_logger.log_started(job_id, job.user_id or 0, len(keywords), num_websites)
        
        total_tasks = num_websites * len(keywords)
        completed_tasks = job.keywords_completed or 0
        website_file_paths = job.output_files or {}
        
        # Initialize completed_keywords if None
        if job.completed_keywords is None:
            job.completed_keywords = {}
        
        # Ensure completed_keywords is a dict (JSON might return different types)
        if not isinstance(job.completed_keywords, dict):
            job.completed_keywords = {}
        
        # Generate content for each website
        for website_index in range(1, num_websites + 1):
            # Check if job has been cancelled before processing each website
            if _is_job_cancelled(job_repository, job_id):
                logger.info(f"Job {job_id} has been cancelled, stopping execution")
                return
            
            # Always refresh and re-initialize completed_keywords at start of each website iteration
            job = job_repository.get_by_id(job_id)
            if not job:
                logger.error(f"Job {job_id} not found during processing")
                return
            
            # Re-initialize completed_keywords after refresh
            if job.completed_keywords is None:
                job.completed_keywords = {}
            if not isinstance(job.completed_keywords, dict):
                job.completed_keywords = {}
            
            # Check which keywords are already completed for this website
            completed_for_website = file_storage.get_completed_keywords(job_id, website_index, keywords)
            completed_keywords_set = set(completed_for_website)
            
            # Initialize tracking if needed - use string key for consistency
            website_key = str(website_index)
            if website_key not in job.completed_keywords:
                job.completed_keywords[website_key] = []
            
            # Ensure the list exists and is actually a list
            if not isinstance(job.completed_keywords[website_key], list):
                job.completed_keywords[website_key] = []
            
            keyword_content_map = {}
            
            # Load existing content for this website
            for keyword in completed_for_website:
                existing_content = file_storage.load_keyword_content(job_id, website_index, keyword)
                if existing_content:
                    keyword_content_map[keyword] = existing_content
                    logger.debug(f"Loaded existing content for keyword '{keyword}' in website {website_index}")
            
            # Process remaining keywords in parallel
            remaining_keywords = [k for k in keywords if k not in completed_keywords_set]
            logger.info(f"Website {website_index}: {len(completed_for_website)} completed, {len(remaining_keywords)} remaining (processing in parallel with {max_workers} workers)")
            
            # Process keywords in parallel using ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all keyword processing tasks
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
                
                # Process completed futures as they finish
                for future in as_completed(future_to_keyword):
                    # Check if job has been cancelled before processing each result
                    if _is_job_cancelled(job_repository, job_id):
                        logger.info(f"Job {job_id} has been cancelled, stopping keyword processing")
                        # Cancel all pending futures (only works for futures that haven't started)
                        cancelled_count = 0
                        for pending_future in future_to_keyword:
                            if not pending_future.done():
                                if pending_future.cancel():
                                    cancelled_count += 1
                        logger.info(f"Cancelled {cancelled_count} pending keyword processing tasks")
                        # Stop processing results - workers already running will finish but we won't process their results
                        return
                    
                    keyword = future_to_keyword[future]
                    
                    # Skip if future was cancelled
                    if future.cancelled():
                        logger.debug(f"Future for keyword '{keyword}' was cancelled, skipping")
                        continue
                    
                    try:
                        processed_keyword, content, success = future.result()
                        keyword_content_map[processed_keyword] = content
                        completed_tasks += 1
                        
                        # Check cancellation again before updating database
                        if _is_job_cancelled(job_repository, job_id):
                            logger.info(f"Job {job_id} has been cancelled, stopping after keyword '{processed_keyword}'")
                            # Cancel all pending futures
                            for pending_future in future_to_keyword:
                                if not pending_future.done():
                                    pending_future.cancel()
                            return
                        
                        # Update job state in main thread (after receiving result from worker)
                        job = job_repository.get_by_id(job_id)
                        if not job:
                            logger.error(f"Job {job_id} not found during keyword processing")
                            continue
                        
                        # Re-initialize completed_keywords after refresh
                        if job.completed_keywords is None:
                            job.completed_keywords = {}
                        if not isinstance(job.completed_keywords, dict):
                            job.completed_keywords = {}
                        
                        # Re-define website_key to ensure it's current
                        website_key = str(website_index)
                        if website_key not in job.completed_keywords:
                            job.completed_keywords[website_key] = []
                        if not isinstance(job.completed_keywords[website_key], list):
                            job.completed_keywords[website_key] = []
                        
                        if processed_keyword not in job.completed_keywords[website_key]:
                            job.completed_keywords[website_key].append(processed_keyword)
                        
                        # Update progress frequently (after each keyword)
                        progress_tracker.update_progress(
                            job_id=job_id,
                            completed_tasks=completed_tasks,
                            total_tasks=total_tasks,
                            keywords_completed=completed_tasks,
                            websites_completed=website_index - 1
                        )
                        
                        # Commit progress to database
                        job.keywords_completed = completed_tasks
                        # Ensure completed_keywords is properly set before saving
                        if job.completed_keywords is None:
                            job.completed_keywords = {}
                        if not isinstance(job.completed_keywords, dict):
                            job.completed_keywords = {}
                        if website_key not in job.completed_keywords:
                            job.completed_keywords[website_key] = []
                        job_repository.update(job)
                        
                        status_text = "successfully" if success else "with errors"
                        logger.debug(f"Completed keyword '{processed_keyword}' for website {website_index} {status_text} ({completed_tasks}/{total_tasks})")
                        
                    except Exception as e:
                        logger.error(f"Unexpected error processing keyword '{keyword}': {e}", exc_info=True)
                        # Mark as completed even on unexpected error to avoid infinite retries
                        completed_tasks += 1
                        # Save error content
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
                            if job.completed_keywords is None:
                                job.completed_keywords = {}
                            if not isinstance(job.completed_keywords, dict):
                                job.completed_keywords = {}
                            website_key = str(website_index)
                            if website_key not in job.completed_keywords:
                                job.completed_keywords[website_key] = []
                            if keyword not in job.completed_keywords[website_key]:
                                job.completed_keywords[website_key].append(keyword)
                            job_repository.update(job)
            
            # Check if job has been cancelled before finalizing website
            if _is_job_cancelled(job_repository, job_id):
                logger.info(f"Job {job_id} has been cancelled, stopping before finalizing website {website_index}")
                return
            
            # Create website file content from all keywords (both existing and new)
            file_content = create_website_file(
                website_index=website_index,
                lang=lang,
                geo=geo,
                keyword_content_map=keyword_content_map
            )
            
            # Save final website file
            file_path = file_storage.save_website_file(
                job_id=job_id,
                website_index=website_index,
                lang=lang,
                geo=geo,
                content=file_content
            )
            website_file_paths[website_index] = file_path
            
            # Update websites completed
            job = job_repository.get_by_id(job_id)
            if job:
                job.websites_completed = website_index
                job.output_files = website_file_paths
                job_repository.update(job)
        
        # Check if job has been cancelled before marking as completed
        if _is_job_cancelled(job_repository, job_id):
            logger.info(f"Job {job_id} has been cancelled, not marking as completed")
            return
        
        # Mark job as completed
        job = job_repository.get_by_id(job_id)
        if job:
            # Double-check cancellation status before final update
            if _is_job_cancelled(job_repository, job_id):
                logger.info(f"Job {job_id} was cancelled during final update, stopping")
                return
            
            job.status = "completed"
            job.progress = 100
            job.websites_completed = num_websites
            job.keywords_completed = completed_tasks
            job.output_files = website_file_paths
            job.completed_at = datetime.utcnow()
            # Ensure completed_keywords is saved (should already be populated, but ensure it's not None)
            if job.completed_keywords is None:
                job.completed_keywords = {}
            job_repository.update(job)
            
            job_logger.log_completed(job_id, job.user_id or 0, num_websites, completed_tasks)
        
    except Exception as e:
        # Mark job as failed, but preserve progress
        error_msg = f"Task failed for job {job_id}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        if job:
            try:
                # Don't mark as failed if we made progress - allow resume
                if job.keywords_completed and job.keywords_completed > 0:
                    job.status = "processing"  # Keep as processing to allow resume
                    logger.info(f"Job {job_id} failed but has progress ({job.keywords_completed} keywords). Can be resumed.")
                else:
                    job.status = "failed"
                
                job.error_message = str(e)
                job_repository.update(job)
                job_logger.log_failed(job_id, job.user_id or 0, str(e))
            except Exception as update_error:
                logger.error(f"Failed to update job status: {update_error}", exc_info=True)
    finally:
        try:
            db.close()
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")

