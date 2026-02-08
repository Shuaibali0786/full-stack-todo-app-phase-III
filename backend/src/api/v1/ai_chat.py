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
    print(f"\n[CHAT ENDPOINT] === NEW REQUEST ===")
    print(f"[CHAT ENDPOINT] User: {current_user.email}")
    print(f"[CHAT ENDPOINT] Message: {message_data.message}")
    try:
        agent_service = AgentService()
        response = await agent_service.process_message(
            message=message_data.message,
            user_id=current_user.id,
            session=session
        )

        # Return response even if chat is unavailable (graceful degradation)
        return AIMessageResponse(
            response=response.get("response", ""),
            actions=response.get("actions", [])
        )

    except ValueError as e:
        # OpenAI API key not configured - return clean error message (200 OK with error text)
        import traceback
        print(f"[CHAT API ERROR] ValueError: {str(e)}")
        print(traceback.format_exc())
        # IMPORTANT: Return 200 instead of 503 to prevent frontend errors
        return AIMessageResponse(
            response="Chat service is currently unavailable. Please configure OPENAI_API_KEY in backend/.env to enable AI features.",
            actions=[]
        )
    except Exception as e:
        # Generic error handling - graceful degradation
        import traceback
        error_str = str(e).lower()
        print(f"[CHAT API ERROR] Exception: {str(e)}")
        print(traceback.format_exc())

        # Return 200 with helpful error message instead of 500/503
        # This prevents chat from breaking the entire app
        if "402" in error_str or "insufficient" in error_str or "credit" in error_str:
            error_msg = "⚠️ Chat service is temporarily unavailable due to API credits. You can still manage tasks using the dashboard."
        elif "503" in error_str:
            error_msg = "⚠️ Chat service is temporarily busy. Please try again in a moment."
        else:
            error_msg = f"⚠️ Chat service encountered an error. Please try again or use the dashboard to manage tasks."

        return AIMessageResponse(
            response=error_msg,
            actions=[]
        )