"""Dependency injection functions for FastAPI."""
from fastapi import BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.job_repository import JobRepository
from app.repositories.log_repository import LogRepository
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.services.job_service import JobService
from app.services.queue import create_queue_service


def get_job_repository(db: Session = Depends(get_db)) -> JobRepository:
    """
    Get JobRepository instance.
    
    Args:
        db: Database session
        
    Returns:
        JobRepository instance
    """
    return JobRepository(db)


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """
    Get UserRepository instance.
    
    Args:
        db: Database session
        
    Returns:
        UserRepository instance
    """
    return UserRepository(db)


def get_session_repository(db: Session = Depends(get_db)) -> SessionRepository:
    """
    Get SessionRepository instance.
    
    Args:
        db: Database session
        
    Returns:
        SessionRepository instance
    """
    return SessionRepository(db)


def get_job_service(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> JobService:
    """
    Get JobService instance.
    
    Args:
        background_tasks: FastAPI BackgroundTasks
        db: Database session
        
    Returns:
        JobService instance
    """
    queue = create_queue_service(background_tasks)
    return JobService(db, queue)


def get_log_repository(db: Session = Depends(get_db)) -> LogRepository:
    """
    Get LogRepository instance.
    
    Args:
        db: Database session
        
    Returns:
        LogRepository instance
    """
    return LogRepository(db)

