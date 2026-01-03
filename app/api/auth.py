"""Authentication API endpoints."""
import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.session import Session as SessionModel
from app.models.user import User
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.utils.logger import get_logger
from app.utils.password import hash_password, verify_password
from app.utils.responses import success_response

logger = get_logger(__name__)

router = APIRouter()


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
    last_login: str | None


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login with username and password.
    
    Returns:
        LoginResponse with token and user info
    """
    try:
        # Find user using repository
        user_repository = UserRepository(db)
        user = user_repository.get_by_username(request.username)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Verify password
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )
    
    # Generate session token
    token = secrets.token_urlsafe(32)
    expires_at = SessionModel.get_expiry_time()
    
    # Create session using repository
    session_repository = SessionRepository(db)
    session = SessionModel(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )
    session_repository.create(session)
    
    # Update last login using repository
    user_repository.update_last_login(user.id)
    
    return LoginResponse(
        token=token,
        user={
            "id": user.id,
            "username": user.username,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None
        }
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout current user (delete session).
    """
    # Delete all sessions for user using repository
    session_repository = SessionRepository(db)
    session_repository.delete_by_user_id(current_user.id)
    
    return success_response(data=None, message="Logged out successfully")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        created_at=current_user.created_at.isoformat() if current_user.created_at else "",
        last_login=current_user.last_login.isoformat() if current_user.last_login else None
    )

