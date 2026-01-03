"""Configuration settings for the application."""
import os
from typing import List, Any, Union
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator, model_validator


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    openrouter_api_key: str = Field(default="", description="OpenRouter API key")
    backend_port: int = Field(default=8000, ge=1, le=65535, description="Backend server port")
    
    # Job Limits
    max_keywords: int = Field(default=1000, ge=1, description="Maximum keywords per job")
    max_websites: int = Field(default=100, ge=1, description="Maximum websites per job")
    
    # Task Configuration
    request_delay_seconds: float = Field(default=2.0, ge=0, description="Delay between API requests")
    task_timeout: int = Field(default=300, ge=1, description="Task timeout in seconds")
    
    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./content_generator.db",
        description="Database connection URL"
    )
    
    # Queue Configuration
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    use_redis: bool = Field(
        default=False,
        description="Whether to use Redis for task queue"
    )
    
    # CORS Configuration
    frontend_url: str = Field(
        description="Frontend URL for CORS (set FRONTEND_URL in .env)"
    )
    cors_origins: Union[str, List[str]] = Field(
        default="http://localhost:3000,http://localhost:3021,http://localhost:5173,http://localhost:5174,http://127.0.0.1:3021,http://127.0.0.1:5173,http://127.0.0.1:3000",
        description="Allowed CORS origins (comma-separated string or list)"
    )
    cors_allow_credentials: bool = Field(default=True, description="Allow credentials in CORS")
    
    # Logging Configuration
    enable_api_logging: bool = Field(default=True, description="Enable API request logging")
    enable_job_logging: bool = Field(default=True, description="Enable job event logging")
    
    # Session Configuration
    session_expiry_hours: int = Field(default=24, ge=1, description="Session expiry in hours")
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        """Parse CORS origins from environment variable."""
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # Handle comma-separated string from .env
            origins = [origin.strip() for origin in v.split(",") if origin.strip()]
            return origins if origins else []
        return []
    
    @field_validator("use_redis", mode="before")
    @classmethod
    def parse_bool(cls, v):
        """Parse boolean from string."""
        if isinstance(v, str):
            return v.lower() == "true"
        return bool(v)
    
    def get_cors_origins(self) -> List[str]:
        """
        Get all CORS origins including frontend_url.
        
        Returns:
            List of allowed CORS origins
        """
        origins = set(self.cors_origins)
        origins.add(self.frontend_url)
        return list(origins)
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env


settings = Settings()

