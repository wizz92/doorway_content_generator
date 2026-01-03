"""User repository for database access."""
from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """Repository for user data access operations."""
    
    def __init__(self, db: Session):
        """
        Initialize repository with database session.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User identifier
            
        Returns:
            User instance or None if not found
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User instance or None if not found
        """
        return self.db.query(User).filter(User.username == username).first()
    
    def update_last_login(self, user_id: int) -> User:
        """
        Update user's last login timestamp.
        
        Args:
            user_id: User identifier
            
        Returns:
            Updated user instance
            
        Raises:
            ValueError: If user not found
        """
        from datetime import datetime
        
        user = self.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")
        
        user.last_login = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def create(self, user: User) -> User:
        """
        Create a new user.
        
        Args:
            user: User instance to create
            
        Returns:
            Created user instance
        """
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
