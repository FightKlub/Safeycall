"""
Configuration management for SaferCall AI Backend
Loads environment variables and provides configuration classes
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    gemini_api_key: str
    openai_api_key: Optional[str] = None
    
    # AWS Configuration
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "us-east-1"
    aws_s3_bucket_name: str
    
    # Database Configuration
    database_url: Optional[str] = None
    redis_url: Optional[str] = None
    
    # Application Settings
    environment: str = "development"
    debug_mode: bool = True
    log_level: str = "INFO"
    max_file_size_mb: int = 10
    
    # Security
    secret_key: str
    allowed_origins: str = "*"
    
    # Twilio Configuration
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_phone_number: Optional[str] = None
    
    # Email Configuration
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # Whisper Model Configuration
    whisper_model_size: str = "base"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    Uses lru_cache to create singleton pattern
    """
    return Settings()


# Scam detection keywords
SCAM_KEYWORDS = [
    "otp", "anydesk", "bank account", "remote access", 
    "atm pin", "credit card", "loan", "prize",
    "tax refund", "irs", "social security", "warrant",
    "suspend", "verify your account", "urgent action required",
    "click here", "confirm your identity", "update payment",
    "wire transfer", "gift card", "bitcoin", "cryptocurrency"
]

# File upload settings
ALLOWED_AUDIO_FORMATS = [".mp3", ".wav", ".m4a", ".ogg", ".flac"]
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "detailed",
            "filename": "logs/safercall.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"],
    },
}
