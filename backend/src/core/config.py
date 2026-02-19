from pydantic_settings import BaseSettings, PydanticBaseSettingsSource
from typing import Optional, Tuple, Type


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Priority order (highest → lowest):
      1. .env file  (so HF Space / Vercel env vars don't accidentally override our DB URL)
      2. Actual environment variables
      3. Default values in this class
    """
    # Database - Neon PostgreSQL
    # asyncpg requires SSL via connect_args, NOT ?sslmode= in the URL
    DATABASE_URL: str = "postgresql+asyncpg://neondb_owner:npg_B3C4FxcwJYGW@ep-jolly-wind-ainmmnu6-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

    SECRET_KEY: str = "todo-app-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Better Auth
    BETTER_AUTH_SECRET: str = "your-better-auth-secret"

    # OpenAI / OpenRouter Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # Agent Configuration
    AGENT_MODEL: str = "anthropic/claude-3.5-sonnet"
    FALLBACK_MODEL: str = "anthropic/claude-3.5-sonnet"

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        # .env file takes priority over OS/container env vars.
        # This ensures that a committed .env (on HF Space) overrides any
        # conflicting environment variable that the platform injects.
        return init_settings, dotenv_settings, env_settings, file_secret_settings


settings = Settings()
