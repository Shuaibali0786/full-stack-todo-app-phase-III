from sqlmodel import SQLModel, Field, Relationship, Column, Enum as SQLEnum
from typing import Optional, TYPE_CHECKING
from datetime import datetime
from enum import Enum
import uuid

if TYPE_CHECKING:
    from .conversation import Conversation


class MessageRole(str, Enum):
    """
    Message role enumeration
    - user: Message from the human user
    - agent: Message from the AI agent
    """
    USER = "user"
    AGENT = "agent"


class MessageBase(SQLModel):
    """
    Base model for Message with common fields
    """
    role: MessageRole = Field(sa_column=Column(SQLEnum(MessageRole), nullable=False))
    content: str = Field(nullable=False, max_length=10000)


class Message(MessageBase, table=True):
    """
    Message model representing a single message in a conversation.

    Per Phase III Constitution:
    - Stores conversation history for stateless context reconstruction
    - Role: 'user' (human input) or 'agent' (AI response)
    - Content limited to 10,000 characters per spec-7
    - Indexed by conversation_id and created_at for efficient retrieval
    """
    __tablename__ = "messages"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    conversation_id: uuid.UUID = Field(
        foreign_key="conversations.id",
        nullable=False,
        index=True
    )
    role: MessageRole = Field(sa_column=Column(SQLEnum(MessageRole), nullable=False))
    content: str = Field(nullable=False, max_length=10000)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        index=True  # Indexed for efficient chronological retrieval
    )

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
