"""Queue service abstraction."""
from app.services.queue.base import QueueInterface
from app.services.queue.factory import create_queue_service

__all__ = ["QueueInterface", "create_queue_service"]

