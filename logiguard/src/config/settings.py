"""Application settings and configuration management."""

from typing import Optional
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.0
    
    # Application Settings
    log_level: str = "INFO"
    data_dir: str = "./data"
    log_dir: str = "./logs"
    
    # Safety Settings
    enable_pii_masking: bool = True
    enable_readonly_enforcement: bool = True
    enable_uncertainty_validation: bool = True
    
    # Performance Settings
    tool_timeout_seconds: int = 5
    max_retries: int = 3
    retry_backoff_factor: int = 2
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def get_data_path(self, filename: str) -> Path:
        """Get full path to data file."""
        return Path(self.data_dir) / filename
    
    def get_log_path(self, filename: str) -> Path:
        """Get full path to log file."""
        return Path(self.log_dir) / filename
    
    def validate_settings(self) -> bool:
        """Validate critical settings."""
        if not self.openai_api_key or self.openai_api_key == "your_api_key_here":
            raise ValueError("OPENAI_API_KEY must be set in .env file")
        
        if self.openai_temperature != 0.0:
            raise ValueError("OPENAI_TEMPERATURE must be 0.0 for deterministic responses")
        
        # Ensure directories exist
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)
        
        return True


# Global settings instance
settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create global settings instance."""
    global settings
    if settings is None:
        settings = Settings()
        settings.validate_settings()
    return settings
