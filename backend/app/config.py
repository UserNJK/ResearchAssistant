"""
Configuration Management
Loads and validates environment variables
"""
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # OpenRouter Configuration
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    
    # Supabase Configuration
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    
    # Application Settings
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "http://localhost:3000"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 10
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    
    # JWT & Authentication (PHASE 6)
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 86400  # 24 hours
    USER_RATE_LIMIT_REQUESTS: int = 100  # Per user, per window
    USER_RATE_LIMIT_WINDOW_SECONDS: int = 3600  # 1 hour
    
    # LLM Models
    PLANNER_MODEL: str = "mistralai/mistral-7b-instruct"
    SUMMARY_MODEL: str = "mistralai/mistral-7b-instruct"
    INSIGHT_MODEL: str = "mistralai/mistral-7b-instruct"
    FORMATTER_MODEL: str = "mistralai/mistral-7b-instruct"
    DEFAULT_FALLBACK_MODEL: str = "mistralai/mistral-7b-instruct"
    
    # LLM Parameters
    LLM_TEMPERATURE: float = 0.4
    LLM_MAX_TOKENS: int = 2000
    LLM_TIMEOUT_SECONDS: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def validate_required_vars(self) -> None:
        """Validate that required environment variables are set"""
        errors = []
        
        if not self.OPENROUTER_API_KEY:
            errors.append("OPENROUTER_API_KEY is required")
        
        if not self.SUPABASE_URL:
            errors.append("SUPABASE_URL is required")
        
        if not self.SUPABASE_SERVICE_ROLE_KEY:
            errors.append("SUPABASE_SERVICE_ROLE_KEY is required")
        
        if errors:
            raise ValueError(
                "Missing required environment variables:\n" + "\n".join(f"  - {e}" for e in errors)
            )


# Initialize settings
settings = Settings()

# Validate on startup (only in production)
if settings.ENVIRONMENT == "production":
    settings.validate_required_vars()
