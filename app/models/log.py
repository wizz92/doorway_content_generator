"""Log models for API and job logging."""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class ApiLog(Base):
    """API request/response logging model."""
    __tablename__ = "api_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    endpoint = Column(String, nullable=False)
    method = Column(String, nullable=False)
    status_code = Column(Integer, nullable=False)
    request_data = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="api_logs")


class JobLog(Base):
    """Job event logging model."""
    __tablename__ = "job_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("jobs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_type = Column(String, nullable=False)  # created, started, progress, completed, failed
    message = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="job_logs")

