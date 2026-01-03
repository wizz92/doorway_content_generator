"""Session repository for database access."""
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.session import Session as SessionModel


class SessionRepository:
    """Repository for session data access operations."""
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def get_by_token(self, token: str) -> Optional[SessionModel]:
        """
        Get session by token.
        
        Args:
            token: Session token
            
        Returns:
            Session instance or None if not found
        """
        return self.db.query(SessionModel).filter(SessionModel.token == token).first()
    
    def get_by_user_id(self, user_id: int) -> List[SessionModel]:
        """
        Get all sessions for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            List of session instances
        """
        return self.db.query(SessionModel).filter(SessionModel.user_id == user_id).all()
    
    def create(self, session: SessionModel) -> SessionModel:
        """
        Create a new session.
        
        Args:
            session: Session instance to create
            
        Returns:
            Created session instance
        """
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def delete_by_user_id(self, user_id: int) -> int:
        """
        Delete all sessions for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Number of sessions deleted
        """
        sessions = self.get_by_user_id(user_id)
        count = len(sessions)
        for session in sessions:
            self.db.delete(session)
        self.db.commit()
        return count
    
    def delete_by_token(self, token: str) -> bool:
        """
        Delete session by token.
        
        Args:
            token: Session token
            
        Returns:
            True if deleted, False if not found
        """
        session = self.get_by_token(token)
        if session:
            self.db.delete(session)
            self.db.commit()
            return True
        return False

