"""FastAPI BackgroundTasks implementation."""
from typing import Callable, Any
from functools import partial
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
        from app.utils.logger import get_logger
        logger = get_logger(__name__)
        
        # Remove job_timeout as BackgroundTasks doesn't support it
        kwargs.pop("job_timeout", None)
        
        # Add job_id to kwargs if provided (task functions may need it)
        if job_id is not None:
            kwargs["job_id"] = job_id
        
        logger.info(f"Enqueuing background task: {func.__name__}, job_id={job_id}, kwargs={list(kwargs.keys())}")
        
        # Wrap the function to ensure errors are logged and properly capture variables
        def wrapped_task(task_func, task_args, task_kwargs, task_job_id):
            try:
                logger.info(f"Executing background task: {task_func.__name__} for job_id={task_job_id}")
                return task_func(*task_args, **task_kwargs)
            except Exception as e:
                logger.error(f"Background task {task_func.__name__} failed for job_id={task_job_id}: {e}", exc_info=True)
                raise
        
        # Use partial to properly bind arguments for the wrapper
        bound_task = partial(wrapped_task, func, args, kwargs, job_id)
        self.background_tasks.add_task(bound_task)
        
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

