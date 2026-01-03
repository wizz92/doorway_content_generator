"""User model for authentication."""
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user")
    api_logs = relationship("ApiLog", back_populates="user")
    job_logs = relationship("JobLog", back_populates="user")

