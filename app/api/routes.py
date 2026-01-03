"""API routes."""
from typing import Any, Dict, List

from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.constants import DEFAULT_JOB_LIST_LIMIT, MAX_JOB_LIST_LIMIT
from app.database import get_db
from app.exceptions import JobNotFoundError, JobAccessDeniedError, JobInvalidStateError
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas import GenerateRequest, JobStatusResponse, JobResponse, JobListResponse
from app.services.file_processor import extract_keywords_from_csv, get_csv_preview, FileProcessingError
from app.services.job_service import JobService
from app.services.queue import create_queue_service
from app.utils.logger import get_logger
from app.utils.responses import success_response

logger = get_logger(__name__)

router = APIRouter()


def _set_no_cache_headers(response: Response) -> None:
    """Set no-cache headers on response."""
    if response:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"


def _validate_jobs_response(jobs: List[JobResponse]) -> None:
    """
    Validate that jobs list contains valid JobResponse objects.
    
    Args:
        jobs: List of jobs to validate
        
    Raises:
        ValueError: If validation fails
    """
    if not isinstance(jobs, list):
        logger.error(f"Expected list, got {type(jobs)}")
        raise ValueError(f"Expected list of jobs, got {type(jobs)}")
    
    for idx, job in enumerate(jobs):
        if not isinstance(job, JobResponse):
            logger.error(f"Item {idx} is not JobResponse, got {type(job)}")
            raise ValueError(f"Expected JobResponse, got {type(job)}")
        if not hasattr(job, 'id') or not hasattr(job, 'status'):
            logger.error(f"JobResponse missing required fields: {job}")
            raise ValueError(f"Invalid JobResponse structure: {job}")


def _convert_jobs_to_dict(jobs: List[JobResponse]) -> List[Dict[str, Any]]:
    """
    Convert JobResponse objects to dictionaries for JSON serialization.
    
    Args:
        jobs: List of JobResponse objects
        
    Returns:
        List of dictionaries
    """
    jobs_dict = []
    for job in jobs:
        if hasattr(job, 'model_dump'):
            jobs_dict.append(job.model_dump())
        elif hasattr(job, 'dict'):
            jobs_dict.append(job.dict())
        else:
            jobs_dict.append(job)
    return jobs_dict


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


@router.post("/upload")
async def upload_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> Dict[str, Any]:
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
        
        return success_response(
            data={
                "job_id": job.id,
                "keywords_count": len(keywords),
                "preview": keywords[:10]  # First 10 keywords as preview
            },
            message="File uploaded successfully"
        )
        
    except ValueError as e:
        raise FileProcessingError(str(e))
    except FileProcessingError:
        raise
    except Exception as e:
        raise FileProcessingError(f"Error processing file: {str(e)}")


@router.get("/upload/preview")
async def preview_csv(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Preview CSV file without creating a job.
    
    Returns preview of keywords.
    """
    try:
        preview, total = get_csv_preview(file, "keyword")
        return success_response(
            data={
                "preview": preview,
                "total_count": total
            },
            message="Preview generated successfully"
        )
    except FileProcessingError:
        raise
    except Exception as e:
        raise FileProcessingError(f"Error processing file: {str(e)}")


@router.post("/generate")
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


@router.get("/job/{job_id}/status", response_model=JobStatusResponse)
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


@router.get("/job/{job_id}/download")
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


@router.get("/jobs")
async def list_jobs(
    limit: int = Query(DEFAULT_JOB_LIST_LIMIT, ge=1, le=MAX_JOB_LIST_LIMIT),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    response: Response = None
):
    """
    List recent jobs for current user.
    
    Returns:
        Dictionary with "jobs" key containing list of job objects
    """
    logger.info(f"/api/jobs endpoint called - user_id={current_user.id}, limit={limit}")
    
    _set_no_cache_headers(response)
    
    job_service = get_job_service(background_tasks, db)
    jobs = job_service.list_jobs(current_user.id, limit)
    
    _validate_jobs_response(jobs)
    jobs_dict = _convert_jobs_to_dict(jobs)
    
    logger.debug(f"Returning {len(jobs_dict)} jobs")
    return {"jobs": jobs_dict}


@router.delete("/job/{job_id}")
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
    return success_response(data=None, message="Job cancelled")
