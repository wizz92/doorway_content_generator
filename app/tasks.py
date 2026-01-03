"""Background tasks for content generation."""
from typing import List, Dict
from datetime import datetime

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


def generate_content_task(
    job_id: str,
    keywords: List[str],
    lang: str,
    geo: str,
    num_websites: int
) -> None:
    """
    Background task to generate content for all keywords and websites.
    
    Args:
        job_id: Job ID
        keywords: List of keywords
        lang: Language code
        geo: Geography code
        num_websites: Number of websites
    """
    logger.info(f"Starting background task for job_id={job_id}, keywords_count={len(keywords)}, lang={lang}, geo={geo}, num_websites={num_websites}")
    
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
        
        job.status = "processing"
        job.total_keywords = len(keywords)
        job = job_repository.update(job)
        
        # Log job started
        job_logger.log_started(job_id, job.user_id or 0, len(keywords), num_websites)
        
        total_tasks = num_websites * len(keywords)
        completed_tasks = 0
        website_file_paths = {}
        
        # Generate content for each website
        for website_index in range(1, num_websites + 1):
            keyword_content_map = {}
            
            for keyword in keywords:
                try:
                    # Generate content
                    content = generator.generate_content_for_keyword(
                        keyword=keyword,
                        lang=lang,
                        geo=geo,
                        website_index=website_index
                    )
                    keyword_content_map[keyword] = content
                    completed_tasks += 1
                    
                    # Update progress
                    progress_tracker.update_progress(
                        job_id=job_id,
                        completed_tasks=completed_tasks,
                        total_tasks=total_tasks,
                        keywords_completed=completed_tasks,
                        websites_completed=website_index - 1
                    )
                    
                except Exception as e:
                    error_msg = f"Error generating content for keyword '{keyword}': {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    keyword_content_map[keyword] = f"<p>Error: {str(e)}</p>"
            
            # Create website file content
            file_content = create_website_file(
                website_index=website_index,
                lang=lang,
                geo=geo,
                keyword_content_map=keyword_content_map
            )
            
            # Save file to filesystem
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
                job_repository.update(job)
        
        # Mark job as completed
        job = job_repository.get_by_id(job_id)
        if job:
            job.status = "completed"
            job.progress = 100
            job.websites_completed = num_websites
            job.keywords_completed = completed_tasks
            # Store file paths instead of file contents
            job.output_files = website_file_paths
            job.completed_at = datetime.utcnow()
            job_repository.update(job)
            
            # Log job completion
            job_logger.log_completed(job_id, job.user_id or 0, num_websites, completed_tasks)
        
    except Exception as e:
        # Mark job as failed
        error_msg = f"Task failed for job {job_id}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        if job:
            try:
                job.status = "failed"
                job.error_message = str(e)
                job_repository.update(job)
                job_logger.log_failed(job_id, job.user_id or 0, str(e))
            except Exception as update_error:
                logger.error(f"Failed to update job status: {update_error}", exc_info=True)
        # Don't re-raise - BackgroundTasks will log it, but we've already handled it
    finally:
        try:
            db.close()
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")

