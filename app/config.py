"""Configuration settings for SMR Monitoring System"""

from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "SMR Safety Monitoring System"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./smr_monitoring.db"
    
    # Email Configuration
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    smtp_use_ssl: bool = False
    mail_from: Optional[str] = None
    mail_from_name: Optional[str] = "SMR Safety Monitoring"
    alert_recipients: List[str] = []
    
    # Monitoring Settings
    data_collection_interval: float = 1.0  # seconds
    anomaly_threshold: float = 0.1  # contamination rate
    max_stored_readings: int = 1000
    max_stored_alerts: int = 100
    
    # ML Model Settings
    model_retrain_interval: int = 3600  # seconds (1 hour)
    training_data_size: int = 1000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
