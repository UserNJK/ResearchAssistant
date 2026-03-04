"""
Configuration Management
Loads and validates environment variables
Compatible with Pydantic v2
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    # =========================
    # Debug & Environment
    # =========================
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # =========================
    # OpenRouter Configuration
    # =========================
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # =========================
    # Supabase Configuration
    # =========================
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""              # ✅ REQUIRED (even if unused)
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # =========================
    # CORS
    # =========================
    CORS_ORIGINS: str = "http://localhost:3000"
    CORS_ORIGIN_REGEX: str = ""

    # =========================
    # Global Rate Limiting
    # =========================
    RATE_LIMIT_REQUESTS: int = 10
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # =========================
    # Authentication (PHASE 6)
    # =========================
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 86400  # 24 hours

    USER_RATE_LIMIT_REQUESTS: int = 100
    USER_RATE_LIMIT_WINDOW_SECONDS: int = 3600

    # =========================
    # LLM Models
    # =========================
    PLANNER_MODEL: str = "mistralai/mistral-7b-instruct"
    SUMMARY_MODEL: str = "meta-llama/llama-3.1-8b-instruct"
    INSIGHT_MODEL: str = "meta-llama/llama-3.1-70b-instruct"
    FORMATTER_MODEL: str = "meta-llama/llama-3.1-70b-instruct"
    # Use a more reliable, low-cost default to avoid provider outages (503)
    # Options: "deepseek/deepseek-chat" or "qwen/qwen-2.5-72b-instruct"
    DEFAULT_FALLBACK_MODEL: str = "qwen/qwen-2.5-72b-instruct"


    # =========================
    # LLM Parameters
    # =========================
    LLM_TEMPERATURE: float = 0.4
    LLM_MAX_TOKENS: int = 2000
    LLM_TIMEOUT_SECONDS: int = 30

    # =========================
    # Pydantic v2 Configuration
    # =========================
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="forbid",  # 🔒 SECURITY: no unknown env vars
    )

    # =========================
    # Validation (Production only)
    # =========================
    def validate_required_vars(self) -> None:
        errors = []

        if not self.OPENROUTER_API_KEY:
            errors.append("OPENROUTER_API_KEY is required")

        if not self.SUPABASE_URL:
            errors.append("SUPABASE_URL is required")

        if not self.SUPABASE_SERVICE_ROLE_KEY:
            errors.append("SUPABASE_SERVICE_ROLE_KEY is required")

        if errors:
            raise ValueError(
                "Missing required environment variables:\n"
                + "\n".join(f"  - {e}" for e in errors)
            )


# =========================
# Initialize Settings
# =========================
settings = Settings()

# Only enforce strict validation in production
if settings.ENVIRONMENT == "production":
    settings.validate_required_vars()
