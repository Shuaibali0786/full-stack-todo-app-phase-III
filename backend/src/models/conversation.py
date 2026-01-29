from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import uuid

if TYPE_CHECKING:
    from .user import User
    from .message import Message


class ConversationBase(SQLModel):
    """
    Base model for Conversation with common fields
    """
    pass


class Conversation(ConversationBase, table=True):
    """
    Conversation model representing a persistent chat session for a user.

    Per Phase III Constitution:
    - One conversation per user (UNIQUE constraint on user_id)
    - Stateless architecture: context reconstructed from messages on every request
    - Used for multi-device continuity and resume-after-restart
    """
    __tablename__ = "conversations"

    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4,
        primary_key=True
    )
    user_id: uuid.UUID = Field(
        foreign_key="users.id",
        nullable=False,
        unique=True,  # One conversation per user (MVP constraint)
        index=True
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )

    # Relationships
    user: "User" = Relationship(back_populates="conversation")
    messages: list["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
