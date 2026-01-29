"""
Conversation Service

Handles CRUD operations for conversations and messages.

Constitutional Compliance:
- Principle III (Stateless Architecture): Context reconstructed from DB every request
- Principle IV (Tool-Only Mutation): This service called by MCP tools only
- Principle V (Clear Responsibility Separation): Pure database layer, no business logic
"""
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..models.conversation import Conversation
from ..models.message import Message, MessageRole
from ..models.user import User


class ConversationService:
    """
    Service for managing conversations and messages.

    Per Phase III Constitution:
    - Stateless: No instance variables, all state from database
    - One conversation per user (enforced by UNIQUE constraint)
    - Context reconstruction on every request
    """

    @staticmethod
    async def get_or_create_conversation(
        user_id: UUID,
        session: AsyncSession
    ) -> Conversation:
        """
        Get existing conversation for user or create new one.

        Args:
            user_id: UUID of authenticated user
            session: Async database session

        Returns:
            Conversation object (existing or newly created)

        Raises:
            ValueError: If user_id is invalid or user doesn't exist
        """
        # Check if conversation exists for user
        query = select(Conversation).where(Conversation.user_id == user_id)
        result = await session.execute(query)
        conversation = result.scalar_one_or_none()

        if conversation:
            # Update timestamp on conversation access
            conversation.updated_at = datetime.utcnow()
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)
            return conversation

        # Verify user exists before creating conversation
        user = await session.get(User, user_id)
        if not user:
            raise ValueError(f"User with id {user_id} does not exist")

        # Create new conversation
        conversation = Conversation(
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        session.add(conversation)
        await session.commit()
        # Refresh to get the generated ID from database
        await session.refresh(conversation)
        return conversation

    @staticmethod
    async def add_message(
        conversation_id: UUID,
        role: MessageRole,
        content: str,
        session: AsyncSession
    ) -> Message:
        """
        Add a message to conversation.

        Args:
            conversation_id: UUID of conversation
            role: MessageRole.USER or MessageRole.AGENT
            content: Message content (max 10,000 characters)
            session: Async database session

        Returns:
            Created Message object

        Raises:
            ValueError: If conversation doesn't exist or content too long
        """
        # Verify conversation exists
        conversation = await session.get(Conversation, conversation_id)
        if not conversation:
            raise ValueError(f"Conversation with id {conversation_id} does not exist")

        # Truncate content if exceeds max length (per spec FR-014)
        max_length = 10000
        if len(content) > max_length:
            content = content[:max_length]

        # Create message
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            created_at=datetime.utcnow()
        )
        session.add(message)

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)

        await session.commit()
        await session.refresh(message)
        return message

    @staticmethod
    async def get_conversation_context(
        conversation_id: UUID,
        session: AsyncSession,
        limit: int = 50
    ) -> List[Message]:
        """
        Retrieve conversation history for context reconstruction.

        Per Principle III (Stateless Architecture):
        - Context reconstructed from database on every request
        - No in-memory caching between requests
        - Retrieves most recent N messages (default 50 per spec FR-007)

        Args:
            conversation_id: UUID of conversation
            limit: Maximum number of recent messages to retrieve (default 50)
            session: Async database session

        Returns:
            List of Message objects in chronological order (oldest first)

        Raises:
            ValueError: If conversation doesn't exist
        """
        # Verify conversation exists
        conversation = await session.get(Conversation, conversation_id)
        if not conversation:
            raise ValueError(f"Conversation with id {conversation_id} does not exist")

        # Query messages in reverse chronological order, limit to N most recent
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        result = await session.execute(query)
        messages = list(result.scalars().all())

        # Reverse to get chronological order (oldest first)
        messages.reverse()
        return messages

    @staticmethod
    async def get_conversation_by_user(
        user_id: UUID,
        session: AsyncSession
    ) -> Optional[Conversation]:
        """
        Get conversation for specific user.

        Args:
            user_id: UUID of user
            session: Async database session

        Returns:
            Conversation object or None if doesn't exist
        """
        query = select(Conversation).where(Conversation.user_id == user_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_conversation(
        conversation_id: UUID,
        session: AsyncSession
    ) -> bool:
        """
        Delete conversation and all associated messages.

        Cascade delete is handled by database foreign key constraint.

        Args:
            conversation_id: UUID of conversation to delete
            session: Async database session

        Returns:
            True if conversation was deleted, False if not found
        """
        conversation = await session.get(Conversation, conversation_id)
        if not conversation:
            return False

        await session.delete(conversation)
        await session.commit()
        return True
