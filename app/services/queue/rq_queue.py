"""RQ (Redis Queue) implementation."""
from typing import Callable, Any
from app.services.queue.base import QueueInterface
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RQQueue(QueueInterface):
    """Redis Queue implementation."""
    
    def __init__(self):
        """Initialize RQ queue."""
        try:
            from redis import Redis
            from rq import Queue
            self.redis_conn = Redis.from_url(settings.redis_url)
            self.queue = Queue(connection=self.redis_conn)
            self._available = True
        except Exception as e:
            logger.warning(f"Redis not available: {e}")
            self._available = False
            self.queue = None
    
    def is_available(self) -> bool:
        """Check if Redis queue is available."""
        return self._available
    
    def enqueue(
        self,
        func: Callable,
        *args,
        job_id: str | None = None,
        **kwargs
    ) -> Any:
        """
        Enqueue a task using RQ.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            job_id: Optional job identifier
            **kwargs: Keyword arguments including job_timeout
            
        Returns:
            RQ job instance
        """
        if not self._available:
            raise RuntimeError("Redis queue is not available")
        
        job_timeout = kwargs.pop("job_timeout", settings.task_timeout)
        return self.queue.enqueue(
            func,
            *args,
            job_timeout=job_timeout,
            **kwargs
        )
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel an RQ job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if cancelled, False otherwise
        """
        if not self._available or not self.queue:
            return False
        
        try:
            from rq.job import Job
            job = Job.fetch(job_id, connection=self.redis_conn)
            job.cancel()
            return True
        except Exception:
            # Try to find job in queue
            try:
                for rq_job in self.queue.jobs:
                    if rq_job.id == job_id or (hasattr(rq_job, 'args') and job_id in str(rq_job.args)):
                        rq_job.cancel()
                        return True
            except Exception:
                pass
            return False

