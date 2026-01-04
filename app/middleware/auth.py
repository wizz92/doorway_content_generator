"""Authentication middleware."""
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.dependencies import get_session_repository, get_user_repository
from app.models.user import User
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session_repository: SessionRepository = Depends(get_session_repository),
    user_repository: UserRepository = Depends(get_user_repository)
) -> User:
    """
    Get current authenticated user from session token.
    
    Args:
        credentials: HTTP authorization credentials
        session_repository: Session repository dependency
        user_repository: User repository dependency
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    # Find session using repository
    session = session_repository.get_by_token(token)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    
    # Check if expired
    if session.is_expired():
        session_repository.delete_by_token(token)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired"
        )
    
    # Get user using repository
    user = user_repository.get_by_id(session.user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Update last login using repository
    user_repository.update_last_login(user.id)
    
    return user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session_repository: SessionRepository = Depends(get_session_repository),
    user_repository: UserRepository = Depends(get_user_repository)
) -> User | None:
    """
    Get current user if authenticated, otherwise return None.
    
    Args:
        credentials: HTTP authorization credentials
        session_repository: Session repository dependency
        user_repository: User repository dependency
        
    Returns:
        User instance if authenticated, None otherwise
    """
    try:
        return await get_current_user(credentials, session_repository, user_repository)
    except HTTPException:
        return None

