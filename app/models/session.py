"""Session model for authentication."""
import os
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from app.database import Base


class Session(Base):
    """Session model for user authentication."""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    @staticmethod
    def get_expiry_time():
        """Get session expiry time (default 24 hours)."""
        hours = int(os.getenv("SESSION_EXPIRY_HOURS", "24"))
        return datetime.utcnow() + timedelta(hours=hours)
    
    def is_expired(self):
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at
