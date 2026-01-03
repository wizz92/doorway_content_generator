"""Background tasks for content generation."""
from typing import List, Dict
from datetime import datetime

from app.database import SessionLocal
from app.repositories.job_repository import JobRepository
from app.services.content_generator import ContentGenerator
from app.services.output_formatter import create_website_file
from app.services.progress_tracker import ProgressTracker
from app.services.job_logger import JobLogger
from app.config import settings


def generate_content_task(
    job_id: str,
    keywords: List[str],
    lang: str,
    geo: str,
    num_websites: int
):
    """
    Background task to generate content for all keywords and websites.
    
    Args:
        job_id: Job ID
        keywords: List of keywords
        lang: Language code
        geo: Geography code
        num_websites: Number of websites
    """
    db = SessionLocal()
    job_repository = JobRepository(db)
    progress_tracker = ProgressTracker(db, job_repository)
    job_logger = JobLogger(db)
    generator = ContentGenerator()
    
    job = None
    
    try:
        # Get job and update status
        job = job_repository.get_by_id(job_id)
        if not job:
            return
        
        job.status = "processing"
        job.total_keywords = len(keywords)
        job = job_repository.update(job)
        
        # Log job started
        job_logger.log_started(job_id, job.user_id or 0, len(keywords), num_websites)
        
        total_tasks = num_websites * len(keywords)
        completed_tasks = 0
        website_files = {}
        
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
                    print(error_msg)
                    keyword_content_map[keyword] = f"<p>Error: {str(e)}</p>"
            
            # Create website file
            website_files[website_index] = create_website_file(
                website_index=website_index,
                lang=lang,
                geo=geo,
                keyword_content_map=keyword_content_map
            )
            
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
            job.output_files = website_files
            job.completed_at = datetime.utcnow()
            job_repository.update(job)
            
            # Log job completion
            job_logger.log_completed(job_id, job.user_id or 0, num_websites, completed_tasks)
        
    except Exception as e:
        # Mark job as failed
        if job:
            job.status = "failed"
            job.error_message = str(e)
            job_repository.update(job)
            job_logger.log_failed(job_id, job.user_id or 0, str(e))
        raise
    finally:
        db.close()

