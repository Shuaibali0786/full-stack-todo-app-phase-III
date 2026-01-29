"""
MCP Server - Stateless Tools for Task Mutations

Constitutional Compliance:
- Principle IV (Tool-Only Mutation Rule): EXCLUSIVE path for database writes
- Principle III (Stateless Architecture): No instance state, all data from database
- Principle V (Clear Responsibility Separation): Pure CRUD operations, no business logic

Per spec-6-mcp-server.md:
- All tools are stateless and transactional
- Input validation and error handling
- 100% test coverage requirement
"""
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from ..models.task import Task
from ..models.user import User
from ..models.priority import Priority
from ..api.v1.sse import broadcast_task_event


class MCPToolError(Exception):
    """Base exception for MCP tool errors"""
    def __init__(self, code: str, message: str, details: Optional[Dict] = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class MCPTools:
    """
    MCP Tools for task management operations.

    All methods are static to enforce stateless architecture.
    Tools are called by Agent Service only (Principle IV).
    """

    @staticmethod
    async def add_task(
        title: str,
        user_id: UUID,
        session: AsyncSession,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
        reminder_time: Optional[datetime] = None,
        priority_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Add a new task for a user.

        Per spec-6 Tool 1 (add_task):
        - Creates task with validation
        - Returns complete task object
        - Transactional (commit or rollback)

        Args:
            title: Task title (required, max 255 chars)
            user_id: User UUID (required)
            session: Async database session
            description: Optional task description (max 5000 chars)
            due_date: Optional due date
            reminder_time: Optional reminder time
            priority_id: Optional priority UUID

        Returns:
            Dict with task data

        Raises:
            MCPToolError: On validation or database errors
        """
        try:
            # Validate user exists
            user = await session.get(User, user_id)
            if not user:
                raise MCPToolError(
                    code="USER_NOT_FOUND",
                    message=f"User with ID {user_id} does not exist",
                    details={"user_id": str(user_id)}
                )

            # Validate title length
            if not title or len(title) > 255:
                raise MCPToolError(
                    code="INVALID_INPUT",
                    message="Title is required and must be max 255 characters",
                    details={"title_length": len(title) if title else 0}
                )

            # Validate description length if provided
            if description and len(description) > 5000:
                raise MCPToolError(
                    code="INVALID_INPUT",
                    message="Description must be max 5000 characters",
                    details={"description_length": len(description)}
                )

            # Validate priority if provided
            if priority_id:
                priority = await session.get(Priority, priority_id)
                if not priority:
                    raise MCPToolError(
                        code="PRIORITY_NOT_FOUND",
                        message=f"Priority with ID {priority_id} does not exist",
                        details={"priority_id": str(priority_id)}
                    )

            # Create task
            task = Task(
                title=title,
                description=description,
                user_id=user_id,
                due_date=due_date,
                reminder_time=reminder_time,
                priority_id=priority_id,
                is_completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            session.add(task)
            await session.commit()
            await session.refresh(task)

            # Prepare task data for return and broadcast
            task_data = {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "is_completed": task.is_completed,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
                "priority_id": str(task.priority_id) if task.priority_id else None,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }

            # Broadcast SSE event for real-time dashboard sync
            await broadcast_task_event(user_id, "TASK_CREATED", task_data)

            return task_data

        except MCPToolError:
            await session.rollback()
            raise
        except Exception as e:
            await session.rollback()
            raise MCPToolError(
                code="DATABASE_ERROR",
                message=f"Failed to create task: {str(e)}",
                details={"error": str(e)}
            )

    @staticmethod
    async def list_tasks(
        user_id: UUID,
        session: AsyncSession,
        completed: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List tasks for a user with optional filtering.

        Per spec-6 Tool 2 (list_tasks):
        - Filters by user_id and completion status
        - Supports pagination
        - Returns tasks in reverse chronological order

        Args:
            user_id: User UUID (required)
            session: Async database session
            completed: Filter by completion status (None = all)
            limit: Max tasks to return (default 50)
            offset: Pagination offset (default 0)

        Returns:
            Dict with tasks list and metadata

        Raises:
            MCPToolError: On validation or database errors
        """
        try:
            # Validate user exists
            user = await session.get(User, user_id)
            if not user:
                raise MCPToolError(
                    code="USER_NOT_FOUND",
                    message=f"User with ID {user_id} does not exist",
                    details={"user_id": str(user_id)}
                )

            # Build query
            query = select(Task).where(Task.user_id == user_id)

            # Apply completion filter
            if completed is not None:
                query = query.where(Task.is_completed == completed)

            # Order by created_at descending (most recent first)
            query = query.order_by(Task.created_at.desc())

            # Apply pagination
            query = query.offset(offset).limit(limit)

            # Execute query
            result = await session.execute(query)
            tasks = result.scalars().all()

            # Convert to dict
            tasks_data = [
                {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "is_completed": task.is_completed,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "reminder_time": task.reminder_time.isoformat() if task.reminder_time else None,
                    "priority_id": str(task.priority_id) if task.priority_id else None,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat()
                }
                for task in tasks
            ]

            return {
                "tasks": tasks_data,
                "count": len(tasks_data),
                "limit": limit,
                "offset": offset
            }

        except MCPToolError:
            raise
        except Exception as e:
            raise MCPToolError(
                code="DATABASE_ERROR",
                message=f"Failed to list tasks: {str(e)}",
                details={"error": str(e)}
            )

    @staticmethod
    async def complete_task(
        task_id: UUID,
        user_id: UUID,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Mark a task as completed.

        Per spec-6 Tool 4 (complete_task):
        - Validates task belongs to user
        - Sets is_completed=True
        - Updates updated_at timestamp

        Args:
            task_id: Task UUID (required)
            user_id: User UUID (required, for authorization)
            session: Async database session

        Returns:
            Dict with updated task data

        Raises:
            MCPToolError: On validation or authorization errors
        """
        try:
            # Get task
            task = await session.get(Task, task_id)
            if not task:
                raise MCPToolError(
                    code="TASK_NOT_FOUND",
                    message=f"Task with ID {task_id} does not exist",
                    details={"task_id": str(task_id)}
                )

            # Verify ownership
            if task.user_id != user_id:
                raise MCPToolError(
                    code="UNAUTHORIZED",
                    message="Task does not belong to user",
                    details={"task_id": str(task_id), "user_id": str(user_id)}
                )

            # Mark as completed
            task.is_completed = True
            task.updated_at = datetime.utcnow()

            session.add(task)
            await session.commit()
            await session.refresh(task)

            return {
                "id": str(task.id),
                "title": task.title,
                "is_completed": task.is_completed,
                "updated_at": task.updated_at.isoformat()
            }

        except MCPToolError:
            await session.rollback()
            raise
        except Exception as e:
            await session.rollback()
            raise MCPToolError(
                code="DATABASE_ERROR",
                message=f"Failed to complete task: {str(e)}",
                details={"error": str(e)}
            )

    @staticmethod
    async def delete_task(
        task_id: UUID,
        user_id: UUID,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Delete a task.

        Per spec-6 Tool 5 (delete_task):
        - Validates task belongs to user
        - Permanently deletes task
        - Returns confirmation

        Args:
            task_id: Task UUID (required)
            user_id: User UUID (required, for authorization)
            session: Async database session

        Returns:
            Dict with deletion confirmation

        Raises:
            MCPToolError: On validation or authorization errors
        """
        try:
            # Get task
            task = await session.get(Task, task_id)
            if not task:
                raise MCPToolError(
                    code="TASK_NOT_FOUND",
                    message=f"Task with ID {task_id} does not exist",
                    details={"task_id": str(task_id)}
                )

            # Verify ownership
            if task.user_id != user_id:
                raise MCPToolError(
                    code="UNAUTHORIZED",
                    message="Task does not belong to user",
                    details={"task_id": str(task_id), "user_id": str(user_id)}
                )

            # Delete task
            await session.delete(task)
            await session.commit()

            return {
                "deleted": True,
                "task_id": str(task_id),
                "title": task.title
            }

        except MCPToolError:
            await session.rollback()
            raise
        except Exception as e:
            await session.rollback()
            raise MCPToolError(
                code="DATABASE_ERROR",
                message=f"Failed to delete task: {str(e)}",
                details={"error": str(e)}
            )

    @staticmethod
    async def update_task_status(
        task_id: UUID,
        status: str,
        user_id: UUID,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Update task status (toggle between pending and completed).

        Per Phase III spec US3 - Toggle Task Status:
        - Validates task belongs to user
        - Sets is_completed based on status ("pending" or "completed")
        - Updates updated_at timestamp

        Args:
            task_id: Task UUID (required)
            status: Target status ("pending" or "completed")
            user_id: User UUID (required, for authorization)
            session: Async database session

        Returns:
            Dict with updated task data

        Raises:
            MCPToolError: On validation or authorization errors
        """
        try:
            # Validate status value
            if status not in ["pending", "completed"]:
                raise MCPToolError(
                    code="INVALID_INPUT",
                    message=f"Status must be 'pending' or 'completed', got '{status}'",
                    details={"status": status}
                )

            # Get task
            task = await session.get(Task, task_id)
            if not task:
                raise MCPToolError(
                    code="TASK_NOT_FOUND",
                    message=f"Task with ID {task_id} does not exist",
                    details={"task_id": str(task_id)}
                )

            # Verify ownership
            if task.user_id != user_id:
                raise MCPToolError(
                    code="UNAUTHORIZED",
                    message="Task does not belong to user",
                    details={"task_id": str(task_id), "user_id": str(user_id)}
                )

            # Update status
            task.is_completed = (status == "completed")
            task.updated_at = datetime.utcnow()

            session.add(task)
            await session.commit()
            await session.refresh(task)

            return {
                "id": str(task.id),
                "title": task.title,
                "is_completed": task.is_completed,
                "status": "completed" if task.is_completed else "pending",
                "updated_at": task.updated_at.isoformat()
            }

        except MCPToolError:
            await session.rollback()
            raise
        except Exception as e:
            await session.rollback()
            raise MCPToolError(
                code="DATABASE_ERROR",
                message=f"Failed to update task status: {str(e)}",
                details={"error": str(e)}
            )

    @staticmethod
    async def find_tasks_by_name(
        query: str,
        user_id: UUID,
        session: AsyncSession
    ) -> List[Dict[str, Any]]:
        """
        Find tasks by partial title match (for disambiguation in delete operations).

        Per Phase III spec US4 - Delete Task:
        - Case-insensitive partial match
        - Returns tasks belonging to user only
        - Used for fuzzy matching in natural language delete commands

        Args:
            query: Search query (partial title match)
            user_id: User UUID (required, for filtering)
            session: Async database session

        Returns:
            List of matching task dicts (id, title, status)

        Raises:
            MCPToolError: On database errors
        """
        try:
            # Query tasks with case-insensitive partial match
            stmt = (
                select(Task)
                .where(Task.user_id == user_id)
                .where(Task.title.ilike(f"%{query}%"))
                .order_by(Task.created_at.desc())
            )
            result = await session.execute(stmt)
            tasks = result.scalars().all()

            return [
                {
                    "id": str(task.id),
                    "title": task.title,
                    "is_completed": task.is_completed,
                    "status": "completed" if task.is_completed else "pending"
                }
                for task in tasks
            ]

        except Exception as e:
            raise MCPToolError(
                code="DATABASE_ERROR",
                message=f"Failed to find tasks: {str(e)}",
                details={"error": str(e)}
            )
