"""FastAPI BackgroundTasks implementation."""
from typing import Callable, Any
from fastapi import BackgroundTasks
from app.services.queue.base import QueueInterface


class BackgroundTasksQueue(QueueInterface):
    """FastAPI BackgroundTasks implementation."""
    
    def __init__(self, background_tasks: BackgroundTasks):
        """
        Initialize background tasks queue.
        
        Args:
            background_tasks: FastAPI BackgroundTasks instance
        """
        self.background_tasks = background_tasks
        self._enqueued_tasks = {}  # Track enqueued tasks
    
    def enqueue(
        self,
        func: Callable,
        *args,
        job_id: str | None = None,
        **kwargs
    ) -> Any:
        """
        Enqueue a task using BackgroundTasks.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            job_id: Optional job identifier
            **kwargs: Keyword arguments (job_timeout is ignored)
            
        Returns:
            Task identifier (job_id or generated)
        """
        # Remove job_timeout as BackgroundTasks doesn't support it
        kwargs.pop("job_timeout", None)
        
        self.background_tasks.add_task(func, *args, **kwargs)
        
        # Return job_id if provided, otherwise generate one
        if job_id:
            self._enqueued_tasks[job_id] = True
            return job_id
        return f"bg_task_{id(self.background_tasks)}"
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a background task (not supported by BackgroundTasks).
        
        Args:
            job_id: Job identifier
            
        Returns:
            False (BackgroundTasks doesn't support cancellation)
        """
        # BackgroundTasks doesn't support cancellation
        # Mark as cancelled in our tracking
        if job_id in self._enqueued_tasks:
            del self._enqueued_tasks[job_id]
        return False

