from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.models.user import User
from src.services.agent_service import AgentService
from src.api.deps import get_current_user
from src.core.database import get_session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


router = APIRouter()


class AIMessageRequest(BaseModel):
    message: str


class AIMessageResponse(BaseModel):
    response: str
    actions: Optional[List[Dict[str, Any]]] = []


@router.post("/chat", response_model=AIMessageResponse)
async def send_ai_message(
    message_data: AIMessageRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Send a message to the AI assistant for natural language task management.

    Phase III Implementation:
    - Uses OpenAI Agents SDK for intent detection
    - Calls MCP tools for all database mutations
    - Persists conversation history via ConversationService
    - Stateless: Context reconstructed from database every request

    Constitutional Compliance:
    - Principle III (Stateless Architecture): ✅
    - Principle IV (Tool-Only Mutation): ✅ Agent → MCP → DB
    - Principle VIII (Agent Behavior Standards): ✅
    """
    try:
        agent_service = AgentService()
        response = await agent_service.process_message(
            message=message_data.message,
            user_id=current_user.id,
            session=session
        )

        return AIMessageResponse(
            response=response.get("response", ""),
            actions=response.get("actions", [])
        )

    except ValueError as e:
        # OpenAI API key not configured
        import traceback
        print(f"[CHAT API ERROR] ValueError: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        # Generic error handling
        import traceback
        print(f"[CHAT API ERROR] Exception: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )