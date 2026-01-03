"""Queue factory for creating appropriate queue implementation."""
from typing import Optional
from fastapi import BackgroundTasks

from app.services.queue.base import QueueInterface
from app.services.queue.rq_queue import RQQueue
from app.services.queue.background_queue import BackgroundTasksQueue
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def create_queue_service(background_tasks: Optional[BackgroundTasks] = None) -> QueueInterface:
    """
    Create appropriate queue service based on configuration.
    
    Args:
        background_tasks: Optional BackgroundTasks instance for fallback
        
    Returns:
        QueueInterface implementation
    """
    if settings.use_redis:
        rq_queue = RQQueue()
        if rq_queue.is_available():
            logger.info("Redis/RQ queue initialized")
            return rq_queue
        else:
            logger.warning("Redis not available, using BackgroundTasks")
    
    if background_tasks is None:
        raise ValueError("BackgroundTasks required when Redis is not available")
    
    logger.info("Using BackgroundTasks queue")
    return BackgroundTasksQueue(background_tasks)

