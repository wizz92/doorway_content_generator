"""Database setup and models."""
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json

from app.config import settings

Base = declarative_base()


class Job(Base):
    """Job model for tracking content generation tasks."""
    __tablename__ = "jobs"
    
    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String, default="queued")  # queued, processing, completed, failed
    keywords = Column(JSON)  # List of keywords
    lang = Column(String)
    geo = Column(String)
    num_websites = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    progress = Column(Integer, default=0)  # 0-100
    websites_completed = Column(Integer, default=0)
    total_keywords = Column(Integer, default=0)
    keywords_completed = Column(Integer, default=0)
    output_files = Column(JSON, nullable=True)  # Store file paths (relative to output directory)
    completed_keywords = Column(JSON, nullable=True)  # Store dict: {website_index: [keyword1, keyword2, ...]}
    
    # Relationships
    user = relationship("User", back_populates="jobs")


# Create engine and session
connect_args = {}
if "sqlite" in settings.database_url:
    connect_args["check_same_thread"] = False
    # Enable WAL mode for better concurrency (allows readers to see writer changes immediately)
    def enable_wal_mode(dbapi_conn, connection_record):
        dbapi_conn.execute("PRAGMA journal_mode=WAL")
    
    engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
    from sqlalchemy import event
    event.listen(engine, "connect", enable_wal_mode)
else:
    engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    # Import all models to ensure they're registered
    from app.models import user, session, log
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # For SQLite, check and add missing columns (migration support)
    if "sqlite" in settings.database_url:
        try:
            conn = engine.raw_connection()
            cursor = conn.cursor()
            
            # Check if completed_keywords column exists
            cursor.execute("PRAGMA table_info(jobs)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if "completed_keywords" not in columns:
                cursor.execute("ALTER TABLE jobs ADD COLUMN completed_keywords TEXT")
                conn.commit()
            
            conn.close()
        except Exception as e:
            # If migration fails, log but don't fail initialization
            import logging
            logging.warning(f"Could not migrate database schema: {e}")


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

