from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1.auth import router as auth_router
from src.api.v1.users import router as users_router

from src.api.v1.tasks import router as tasks_router
from src.api.v1.priorities import router as priorities_router
from src.api.v1.tags import router as tags_router
from src.api.v1.ai_chat import router as ai_chat_router
from src.api.v1.sse import router as sse_router
from src.core.database import create_tables, sync_engine
from src.core.seed_data import seed_default_data


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application
    """
    app = FastAPI(
        title="Todo Application API",
        description="API for the Evolution of Todo application",
        version="1.0.0",
        redirect_slashes=False,  # Prevent query param loss on redirects
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:3001",
            "https://shuaibali-todo-backend.hf.space",
            "https://*.vercel.app",
            "https://*.hf.space",
        ],
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routers
    # Note: Using consistent trailing slash handling with redirect_slashes=False
    app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
    app.include_router(users_router, prefix="/api/v1", tags=["users"])
    app.include_router(tasks_router, prefix="/api/v1/tasks", tags=["tasks"])
    app.include_router(priorities_router, prefix="/api/v1/priorities", tags=["priorities"])
    app.include_router(tags_router, prefix="/api/v1/tags", tags=["tags"])
    app.include_router(ai_chat_router, prefix="/api/v1", tags=["ai"])
    app.include_router(sse_router, prefix="/api/v1/sse", tags=["sse"])

    @app.on_event("startup")
    def startup_event():
        """Create database tables and seed default data on startup"""
        try:
            # Call sync version of create_tables
            from sqlmodel import SQLModel
            from src.models.user import User
            from src.models.task import Task
            from src.models.priority import Priority
            from src.models.tag import Tag
            from src.models.task_tag import TaskTag
            from src.models.recurring_task import RecurringTask
            from src.models.task_instance import TaskInstance
            # Phase III models
            from src.models.conversation import Conversation
            from src.models.message import Message

            # Create tables using sync engine
            SQLModel.metadata.create_all(sync_engine)

            # Seed default data
            seed_default_data()
            print("Startup: DB init and seed completed successfully")
        except Exception as e:
            # Log but don't crash — server still starts; DB ops will fail at request time
            print(f"Startup warning: DB init failed ({e}). Server starting anyway.")

    return app


app = create_app()


@app.get("/")
def read_root():
    """
    Root endpoint for health check
    """
    return {"message": "Todo Application API is running!"}


@app.get("/health")
def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "todo-api"}