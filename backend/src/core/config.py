from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    # Database
    DATABASE_URL: str = "sqlite:///./todo_app.db"
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Better Auth
    BETTER_AUTH_SECRET: str = "your-better-auth-secret"

    # OpenAI / OpenRouter Configuration
    OPENAI_API_KEY: Optional[str] = None  # Used for both OpenAI and OpenRouter
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # Phase III - Agent Configuration
    # For OpenRouter, use format: "openai/gpt-4-turbo" or "anthropic/claude-3-sonnet"
    AGENT_MODEL: str = "openai/gpt-4-turbo"
    FALLBACK_MODEL: str = "openai/gpt-4-turbo"

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100

    class Config:
        env_file = ".env"


settings = Settings()