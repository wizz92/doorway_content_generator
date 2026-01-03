"""User-related schemas."""
from typing import Optional
from pydantic import BaseModel

from app.models.user import User


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


class LoginResponse(BaseModel):
    """Login response model."""
    token: str
    user: dict


class UserResponse(BaseModel):
    """User response model."""
    id: int
    username: str
    created_at: str
    last_login: Optional[str] = None
    
    @classmethod
    def from_orm(cls, user: User) -> "UserResponse":
        """
        Create UserResponse from User model.
        
        Args:
            user: User model instance
            
        Returns:
            UserResponse instance
        """
        return cls(
            id=user.id,
            username=user.username,
            created_at=user.created_at.isoformat() if user.created_at else "",
            last_login=user.last_login.isoformat() if user.last_login else None
        )

