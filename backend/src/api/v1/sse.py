"""
Server-Sent Events (SSE) API for Real-Time Dashboard Sync

Constitutional Compliance:
- Principle IX (Real-Time Sync): SSE for unidirectional server → client updates
- Research decision: SSE chosen over WebSocket for simplicity

Per spec US5 - Dashboard Real-Time Sync:
- Broadcasts TASK_CREATED, TASK_UPDATED, TASK_DELETED events
- User-specific streams (authenticated)
- Auto-reconnect with event replay support
- Heartbeat every 30s to maintain connection
"""
import asyncio
import json
from typing import AsyncGenerator, Dict, Any, Set
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from sse_starlette.sse import EventSourceResponse

from src.models.user import User
from src.api.deps import get_current_user_sse
from src.core.database import get_session


router = APIRouter()

# Global event queue for each connected user
# Format: {user_id: set(asyncio.Queue)}
_user_queues: Dict[UUID, Set[asyncio.Queue]] = {}


def get_user_queues(user_id: UUID) -> Set[asyncio.Queue]:
    """Get or create queue set for user."""
    if user_id not in _user_queues:
        _user_queues[user_id] = set()
    return _user_queues[user_id]


async def broadcast_task_event(
    user_id: UUID,
    event_type: str,
    task_data: Dict[str, Any]
):
    """
    Broadcast task event to all connected clients for a user.

    Per spec contracts/websocket.yaml event types:
    - TASK_CREATED: New task added
    - TASK_UPDATED: Task status changed
    - TASK_DELETED: Task removed

    Args:
        user_id: User UUID to send event to
        event_type: Event type (TASK_CREATED, TASK_UPDATED, TASK_DELETED)
        task_data: Task data dict
    """
    queues = get_user_queues(user_id)

    # Create event payload
    event = {
        "event": event_type,
        "data": task_data,
        "timestamp": datetime.utcnow().isoformat()
    }

    # Broadcast to all connected clients for this user
    for queue in list(queues):  # Use list() to avoid modification during iteration
        try:
            await queue.put(event)
        except Exception as e:
            print(f"[SSE] Error broadcasting to queue: {e}")
            # Remove dead queue
            queues.discard(queue)


async def event_generator(
    user_id: UUID,
    queue: asyncio.Queue,
    request: Request
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Generate SSE events for client.

    Per spec FR-010 (Real-Time Sync):
    - Yields events from queue
    - Sends heartbeat every 30s
    - Handles client disconnect gracefully

    Args:
        user_id: User UUID for filtering events
        queue: Event queue for this client
        request: FastAPI request object (for disconnect detection)

    Yields:
        SSE event dicts with event and data fields
    """
    try:
        while True:
            # Check if client disconnected
            if await request.is_disconnected():
                print(f"[SSE] Client disconnected for user {user_id}")
                break

            try:
                # Wait for event with timeout (30s for heartbeat)
                event = await asyncio.wait_for(queue.get(), timeout=30.0)

                # Yield event to client
                yield {
                    "event": event["event"],
                    "data": json.dumps(event["data"])
                }

            except asyncio.TimeoutError:
                # No events in 30s - send heartbeat
                yield {
                    "event": "HEARTBEAT",
                    "data": json.dumps({
                        "timestamp": datetime.utcnow().isoformat()
                    })
                }

    except asyncio.CancelledError:
        print(f"[SSE] Event generator cancelled for user {user_id}")
    finally:
        # Cleanup: remove queue from user's queue set
        queues = get_user_queues(user_id)
        queues.discard(queue)
        print(f"[SSE] Cleaned up queue for user {user_id}, remaining: {len(queues)}")


@router.get("/tasks")
async def task_events(
    request: Request,
    current_user: User = Depends(get_current_user_sse),
    session: AsyncSession = Depends(get_session)
):
    """
    SSE endpoint for real-time task updates.

    Per spec US5 - Dashboard Real-Time Sync:
    - Authenticated endpoint (requires JWT)
    - User-specific event stream
    - Auto-reconnect support via EventSource
    - Heartbeat every 30s

    Usage (Frontend):
    ```javascript
    const eventSource = new EventSource('/api/v1/sse/tasks', {
        headers: { Authorization: `Bearer ${token}` }
    });

    eventSource.addEventListener('TASK_CREATED', (e) => {
        const task = JSON.parse(e.data);
        // Update UI
    });
    ```

    Returns:
        StreamingResponse with SSE events
    """
    print(f"[SSE] New connection from user {current_user.id}")

    # Create queue for this client
    queue = asyncio.Queue()

    # Register queue for user
    queues = get_user_queues(current_user.id)
    queues.add(queue)
    print(f"[SSE] Registered queue for user {current_user.id}, total: {len(queues)}")

    # Return SSE stream
    return EventSourceResponse(
        event_generator(current_user.id, queue, request),
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


# Export broadcast function for use in MCP tools
__all__ = ["router", "broadcast_task_event"]
