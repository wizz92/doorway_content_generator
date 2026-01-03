"""API routes."""
from typing import List
from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.file_processor import extract_keywords_from_csv, get_csv_preview, FileProcessingError
from app.services.job_service import JobService
from app.services.queue import create_queue_service
from app.schemas import GenerateRequest, JobStatusResponse, JobResponse, JobListResponse
from app.middleware.auth import get_current_user
from app.models.user import User
from app.exceptions import JobNotFoundError, JobAccessDeniedError, JobInvalidStateError

router = APIRouter()


def get_job_service(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> JobService:
    """
    Dependency to get JobService instance.
    
    Args:
        background_tasks: FastAPI BackgroundTasks
        db: Database session
        
    Returns:
        JobService instance
    """
    queue = create_queue_service(background_tasks)
    return JobService(db, queue)


@router.post("/api/upload")
async def upload_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Upload CSV file with keywords.
    
    Returns job ID and keyword count.
    """
    try:
        # Extract keywords
        keywords = extract_keywords_from_csv(file, "keyword")
        
        # Create job service and create job
        job_service = get_job_service(background_tasks, db)
        job = job_service.create_job(current_user.id, keywords)
        
        return {
            "job_id": job.id,
            "keywords_count": len(keywords),
            "preview": keywords[:10]  # First 10 keywords as preview
        }
        
    except ValueError as e:
        raise FileProcessingError(str(e))
    except FileProcessingError:
        raise
    except Exception as e:
        raise FileProcessingError(f"Error processing file: {str(e)}")


@router.get("/api/upload/preview")
async def preview_csv(file: UploadFile = File(...)):
    """
    Preview CSV file without creating a job.
    
    Returns preview of keywords.
    """
    try:
        preview, total = get_csv_preview(file, "keyword")
        return {
            "preview": preview,
            "total_count": total
        }
    except FileProcessingError:
        raise
    except Exception as e:
        raise FileProcessingError(f"Error processing file: {str(e)}")


@router.post("/api/generate")
async def generate_content(
    request: GenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start content generation for a job.
    
    Returns job status.
    """
    job_service = get_job_service(background_tasks, db)
    return job_service.start_generation(request, current_user.id)


@router.get("/api/job/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Get status of a job.
    """
    job_service = get_job_service(background_tasks, db)
    return job_service.get_job_status(job_id, current_user.id)


@router.get("/api/job/{job_id}/download")
async def download_job_results(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Download generated content files as ZIP archive.
    """
    job_service = get_job_service(background_tasks, db)
    zip_content = job_service.download_results(job_id, current_user.id)
    
    # Return as streaming response
    return StreamingResponse(
        iter([zip_content]),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=content-{job_id}.zip"
        }
    )


@router.get("/api/jobs")
async def list_jobs(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    response: Response = None
):
    """
    List recent jobs for current user.
    Returns a dictionary with "jobs" key containing list of job objects (NOT logs!).
    
    This endpoint is at /api/jobs (NOT /api/logs/jobs).
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"✅ /api/jobs endpoint called (NOT /api/logs/jobs) - user_id={current_user.id}, limit={limit}")
    
    # Prevent caching - ensure fresh responses
    if response:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    
    job_service = get_job_service(background_tasks, db)
    jobs = job_service.list_jobs(current_user.id, limit)
    
    # Defensive check: ensure we're returning a list of JobResponse, not logs
    if not isinstance(jobs, list):
        logger.error(f"❌ ERROR: Expected list, got {type(jobs)}")
        raise ValueError(f"Expected list of jobs, got {type(jobs)}")
    
    # Verify each item is a JobResponse (has id and status fields)
    for idx, job in enumerate(jobs):
        if not isinstance(job, JobResponse):
            logger.error(f"❌ ERROR: Item {idx} is not JobResponse, got {type(job)}")
            raise ValueError(f"Expected JobResponse, got {type(job)}")
        if not hasattr(job, 'id') or not hasattr(job, 'status'):
            logger.error(f"❌ ERROR: JobResponse missing required fields: {job}")
            raise ValueError(f"Invalid JobResponse structure: {job}")
    
    # Return as dictionary with "jobs" key (NOT "logs")
    logger.info(f"✅ /api/jobs returning {len(jobs)} JobResponse objects in 'jobs' key (NOT logs!)")
    # Convert JobResponse objects to dicts for JSON serialization
    # Try model_dump() for Pydantic v2, fallback to dict() for v1
    jobs_dict = []
    for job in jobs:
        if hasattr(job, 'model_dump'):
            jobs_dict.append(job.model_dump())
        elif hasattr(job, 'dict'):
            jobs_dict.append(job.dict())
        else:
            # If it's already a dict, use it directly
            jobs_dict.append(job)
    
    # CRITICAL: Return with "jobs" key, NOT "logs" key
    # This is the /api/jobs endpoint - it MUST return {"jobs": [...]}
    # DO NOT use "logs" key - that's for /api/logs/jobs endpoint only!
    
    # Create the response dictionary - explicitly use "jobs" key
    result = {}
    result["jobs"] = jobs_dict  # Explicitly set "jobs" key
    
    # CRITICAL: Ensure "logs" key is NOT present
    if "logs" in result:
        logger.error(f"❌ CRITICAL ERROR: Response contains 'logs' key! Removing it...")
        del result["logs"]
    
    # Final verification - ensure we're returning "jobs" not "logs"
    if "jobs" not in result:
        logger.error(f"❌ CRITICAL ERROR: Response missing 'jobs' key!")
        raise ValueError("Response must contain 'jobs' key, not 'logs'")
    
    # Verify the structure one more time before returning
    assert "jobs" in result, "Response must have 'jobs' key"
    assert "logs" not in result, "Response must NOT have 'logs' key - this is /api/jobs, not /api/logs/jobs!"
    assert isinstance(result["jobs"], list), "jobs must be a list"
    
    # Log the exact response structure for debugging
    logger.info(f"✅ Verified response structure: keys={list(result.keys())}, jobs_count={len(result['jobs'])}")
    logger.info(f"✅ Returning response from /api/jobs with 'jobs' key (NOT 'logs'): {list(result.keys())}")
    
    # CRITICAL: Return a dictionary with "jobs" key - this is the ONLY correct format for /api/jobs
    # This endpoint MUST return {"jobs": [...]} and NEVER {"logs": [...]}
    # Explicitly construct the response to ensure "jobs" key is used
    final_response = dict()
    final_response["jobs"] = jobs_dict  # Explicitly set "jobs" key
    
    # Verify "logs" is NOT in the response
    if "logs" in final_response:
        logger.error(f"❌ FATAL ERROR: 'logs' key found in response! This should NEVER happen!")
        # Remove logs and ensure only jobs is present
        final_response = {"jobs": jobs_dict}
    
    # Double-check the structure
    assert "jobs" in final_response, "Response MUST have 'jobs' key"
    assert "logs" not in final_response, "Response MUST NOT have 'logs' key"
    assert isinstance(final_response["jobs"], list), "jobs must be a list"
    
    logger.info(f"✅ Final response structure verified: keys={list(final_response.keys())}")
    logger.info(f"✅ This is from /api/jobs endpoint - returning with 'jobs' key")
    
    # Add a debug marker to verify this endpoint is being called
    # This will help identify if the wrong endpoint is being hit
    print(f"\n{'='*80}")
    print(f"🔵 /api/jobs ENDPOINT CALLED - Returning {{'jobs': [...]}}")
    print(f"   Response keys: {list(final_response.keys())}")
    print(f"   Jobs count: {len(final_response['jobs'])}")
    print(f"{'='*80}\n")
    
    # Return the response - MUST have "jobs" key, NEVER "logs"
    return final_response


@router.delete("/api/job/{job_id}")
async def cancel_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Cancel a job (if queued or processing).
    """
    job_service = get_job_service(background_tasks, db)
    job_service.cancel_job(job_id, current_user.id)
    return {"message": "Job cancelled"}
