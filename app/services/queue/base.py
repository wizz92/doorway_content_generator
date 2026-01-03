"""Base queue interface."""
from abc import ABC, abstractmethod
from typing import Callable, Any


class QueueInterface(ABC):
    """Abstract interface for task queue implementations."""
    
    @abstractmethod
    def enqueue(
        self,
        func: Callable,
        *args,
        job_id: str | None = None,
        **kwargs
    ) -> Any:
        """
        Enqueue a task for execution.
        
        Args:
            func: Function to execute
            *args: Positional arguments for function
            job_id: Optional job identifier
            **kwargs: Keyword arguments for function
            
        Returns:
            Job identifier or task object
        """
        pass
    
    @abstractmethod
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a queued job.
        
        Args:
            job_id: Job identifier to cancel
            
        Returns:
            True if job was cancelled, False otherwise
        """
        pass

