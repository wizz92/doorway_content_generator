"""Authentication middleware."""
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.models.session import Session as SessionModel
from app.models.user import User


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from session token.
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    # Find session
    session = db.query(SessionModel).filter(SessionModel.token == token).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    
    # Check if expired
    if session.is_expired():
        db.delete(session)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired"
        )
    
    # Get user
    user = db.query(User).filter(User.id == session.user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return user


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User | None:
    """
    Get current user if authenticated, otherwise return None.
    """
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None

