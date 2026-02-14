from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import create_engine as sync_create_engine
from .config import settings
from typing import AsyncGenerator


# SSL configuration for Neon PostgreSQL
# Note: psycopg2 (sync) uses "sslmode", asyncpg (async) uses "ssl" as boolean or SSLContext
sync_ssl_args = {
    "sslmode": "require"
}

# For asyncpg, ssl=True enables SSL with default verification
# Neon requires SSL, so we set ssl=True
async_ssl_args = {
    "ssl": True
}

# Strip ?sslmode=require from URL — asyncpg rejects it; SSL is handled via connect_args
_clean_async_url = settings.DATABASE_URL.split("?")[0]

# Create sync engine for table creation (uses psycopg2)
sync_url = _clean_async_url.replace("postgresql+asyncpg://", "postgresql://") + "?sslmode=require"
sync_engine = sync_create_engine(
    sync_url,
    echo=False,  # Set to True for SQL query logging
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args=sync_ssl_args
)

# Create async engine for async operations (uses asyncpg)
async_engine = create_async_engine(
    _clean_async_url,
    echo=False,  # Set to False to reduce log noise
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args=async_ssl_args
)

# Use the async engine as the main engine for the app
engine = async_engine


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async database session for dependency injection.

    CRITICAL: expire_on_commit=False prevents SQLAlchemy from expiring
    objects after commit, which would trigger lazy loads and cause
    MissingGreenlet errors when accessing attributes outside the
    original async context.
    """
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


async def create_tables(db_engine=None):
    """
    Create all database tables synchronously (since SQLModel requires sync operation)
    """
    if db_engine is None:
        db_engine = sync_engine

    # Import all models to register them with SQLModel
    from ..models.user import User
    from ..models.task import Task
    from ..models.priority import Priority
    from ..models.tag import Tag
    from ..models.task_tag import TaskTag
    from ..models.recurring_task import RecurringTask
    from ..models.task_instance import TaskInstance
    from ..models.password_reset import PasswordResetToken
    # Phase III models
    from ..models.conversation import Conversation
    from ..models.message import Message

    # Create tables using the sync engine
    SQLModel.metadata.create_all(db_engine)