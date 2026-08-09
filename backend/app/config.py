import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration using environment variables."""
    
    # Database
    DATABASE_URL: str
    
    # AI
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-3.5-flash"
    
    # Identity
    CANDIDATE_ID: str
    
    # CORS
    FRONTEND_URL: str
    
    # Application
    APP_NAME: str = "Sales Inbox Task Router"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()


settings = get_settings()
