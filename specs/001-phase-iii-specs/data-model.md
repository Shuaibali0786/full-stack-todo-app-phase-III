# Data Model: TaskFlow AI

**Feature**: TaskFlow AI - Intelligent Task Assistant
**Date**: 2026-01-27
**Phase**: Phase 1 (Design)

## Overview

This document defines the database schema and data models for TaskFlow AI Phase III. The design extends the existing Phase II schema with conversation history tables while preserving all existing tables unchanged (backward compatibility mandate).

---

## Schema Diagram

```text
┌──────────────────────────────────────────────────────────────┐
│                    PHASE II (Existing)                       │
└──────────────────────────────────────────────────────────────┘

┌─────────────────┐         ┌─────────────────┐
│     users       │◄────────│     tasks       │
├─────────────────┤         ├─────────────────┤
│ id (PK)         │1       *│ id (PK)         │
│ email           │         │ user_id (FK)    │
│ password_hash   │         │ title           │
│ created_at      │         │ description     │
│ updated_at      │         │ is_completed    │
└─────────────────┘         │ due_date        │
                            │ reminder_time   │
                            │ priority_id (FK)│
                            │ created_at      │
                            │ updated_at      │
                            └─────────────────┘
                                     │
                                     │*
                            ┌─────────────────┐
                            │   priorities    │
                            ├─────────────────┤
                            │ id (PK)         │
                            │ name            │
                            │ level           │
                            └─────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                    PHASE III (New)                           │
└──────────────────────────────────────────────────────────────┘

┌─────────────────┐         ┌──────────────────┐
│     users       │◄────────│  conversations   │
│  (existing)     │1       *│                  │
└─────────────────┘         ├──────────────────┤
                            │ id (PK)          │
                            │ user_id (FK)     │
                            │ created_at       │
                            │ updated_at       │
                            └─────────┬────────┘
                                      │1
                                      │
                                      │*
                            ┌──────────────────┐
                            │    messages      │
                            ├──────────────────┤
                            │ id (PK)          │
                            │ conversation_id  │
                            │   (FK)           │
                            │ role             │
                            │ content          │
                            │ created_at       │
                            └──────────────────┘
```

---

## Phase II Tables (Existing - NO CHANGES)

### users
**Purpose**: User accounts with authentication credentials (Phase II)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique user identifier |
| email | String(255) | UNIQUE, NOT NULL | User email address |
| password_hash | String | NOT NULL | Bcrypt hashed password |
| created_at | DateTime | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| updated_at | DateTime | NOT NULL, DEFAULT NOW() | Last account update timestamp |

**Indexes**: `email` (unique)
**Phase III Impact**: None (read-only usage for user_id foreign keys)

---

### tasks
**Purpose**: Todo items created by users (Phase II)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique task identifier |
| user_id | UUID | FOREIGN KEY (users.id), NOT NULL | Task owner |
| title | String(255) | NOT NULL | Task title (immutable in Phase III) |
| description | Text | NULL | Task details (optional) |
| is_completed | Boolean | NOT NULL, DEFAULT FALSE | Completion status |
| due_date | DateTime | NULL | Optional due date |
| reminder_time | DateTime | NULL | Optional reminder |
| priority_id | UUID | FOREIGN KEY (priorities.id), NULL | Task priority |
| created_at | DateTime | NOT NULL, DEFAULT NOW() | Task creation timestamp |
| updated_at | DateTime | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**:
- `user_id` (for user isolation queries)
- `is_completed` (for status filtering)

**Phase III Mapping**:
- `is_completed = False` → Status "pending"
- `is_completed = True` → Status "completed"

**Phase III Operations**:
- CREATE: Via `create_task` MCP tool
- READ: Via `list_tasks`, `find_tasks_by_name` MCP tools
- UPDATE: Only `is_completed` toggle via `update_task_status` MCP tool (title immutable)
- DELETE: Via `delete_task` MCP tool

---

### priorities
**Purpose**: Task priority levels (Phase II)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique priority identifier |
| name | String(50) | NOT NULL | Priority name (e.g., "High", "Medium") |
| level | Integer | NOT NULL | Numeric priority level |

**Phase III Impact**: None (optional field in tasks, not used by AI chat)

---

## Phase III Tables (New)

### conversations
**Purpose**: Conversation sessions between users and TaskFlow AI

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid4() | Unique conversation identifier |
| user_id | UUID | FOREIGN KEY (users.id), NOT NULL | Conversation owner (enforces user isolation) |
| created_at | DateTime | NOT NULL, DEFAULT NOW() | Conversation start time |
| updated_at | DateTime | NOT NULL, DEFAULT NOW() | Last message timestamp |

**Indexes**:
- `user_id` (for user isolation queries)

**Constraints**:
- One active conversation per user (UNIQUE constraint on `user_id` where `active = TRUE`)
- Cascade delete: Delete all messages when conversation deleted

**Lifecycle**:
1. **Creation**: First AI chat message creates conversation via `get_or_create_conversation()`
2. **Updates**: `updated_at` refreshed on every new message
3. **Deletion**: Manual cleanup (future: archive old conversations after 30 days)

**SQLModel Definition** (`backend/src/models/conversation.py`):
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
```

---

### messages
**Purpose**: Individual chat messages within conversations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, DEFAULT uuid4() | Unique message identifier |
| conversation_id | UUID | FOREIGN KEY (conversations.id), NOT NULL | Parent conversation |
| role | Enum('user', 'assistant') | NOT NULL | Message sender (user or AI) |
| content | Text | NOT NULL | Message text content |
| created_at | DateTime | NOT NULL, DEFAULT NOW() | Message timestamp |

**Indexes**:
- `conversation_id` (for fetching conversation history)
- `created_at` (for chronological ordering)

**Constraints**:
- `role` must be either 'user' or 'assistant' (ENUM or CHECK constraint)
- `content` max length: 10,000 characters (validation in API layer)

**Lifecycle**:
1. **Creation**: Every user message and AI response creates a new message record
2. **Retrieval**: Load last 10 messages via `ORDER BY created_at DESC LIMIT 10`
3. **Deletion**: Cascade delete when parent conversation deleted

**SQLModel Definition** (`backend/src/models/message.py`):
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        nullable=False,
        index=True
    )
    role: MessageRole = Field(nullable=False)
    content: str = Field(nullable=False, max_length=10000)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")
```

---

## Data Validation Rules

### Input Validation (API Layer)

| Field | Validation Rule | Error Message |
|-------|-----------------|---------------|
| `task.title` | 1-500 characters, no leading/trailing whitespace | "Task title must be 1-500 characters" |
| `task.title` | Sanitize HTML/JS (XSS prevention) | "Task title contains invalid characters" |
| `message.content` | 1-10,000 characters | "Message too long (max 10,000 characters)" |
| `message.role` | Must be 'user' or 'assistant' | "Invalid message role" |
| `conversation.user_id` | Must match authenticated user | "Unauthorized access" |

### Business Rules

1. **User Isolation**:
   - All queries filtered by `user_id = current_user.id`
   - No cross-user task access (enforced in MCP tools)

2. **Task Title Immutability**:
   - Once task created, `title` field is READ-ONLY
   - Only `is_completed` can be updated via `update_task_status`

3. **Conversation Context**:
   - Load last 10 messages per user per request
   - Older messages ignored (no summarization in Phase III)

4. **Message Ordering**:
   - Always return messages in chronological order (oldest first)
   - Database query: `ORDER BY created_at ASC` (after reversing LIMIT 10 DESC)

---

## Database Migrations

### Migration 001: Create Conversations Table
```sql
-- File: backend/src/migrations/001_create_conversations.sql

CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
```

### Migration 002: Create Messages Table
```sql
-- File: backend/src/migrations/002_create_messages.sql

CREATE TYPE message_role AS ENUM ('user', 'assistant');

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role message_role NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

**Migration Execution**:
```bash
# Apply migrations (backend/src/main.py startup event)
python -m alembic upgrade head
```

---

## Sample Data (Development/Testing)

### Sample Conversation
```sql
-- User: alice@example.com (user_id: 550e8400-e29b-41d4-a716-446655440001)

INSERT INTO conversations (id, user_id, created_at, updated_at) VALUES
('650e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', '2026-01-27 10:00:00', '2026-01-27 10:05:00');

INSERT INTO messages (conversation_id, role, content, created_at) VALUES
('650e8400-e29b-41d4-a716-446655440001', 'user', 'add task buy groceries', '2026-01-27 10:00:00'),
('650e8400-e29b-41d4-a716-446655440001', 'assistant', '✅ Task created: "buy groceries" (ID: abc-123, Status: pending)', '2026-01-27 10:00:02'),
('650e8400-e29b-41d4-a716-446655440001', 'user', 'show tasks', '2026-01-27 10:02:00'),
('650e8400-e29b-41d4-a716-446655440001', 'assistant', 'You have 1 task:\n1. buy groceries (ID: abc-123, Status: pending, Created: 10:00 AM)', '2026-01-27 10:02:01'),
('650e8400-e29b-41d4-a716-446655440001', 'user', 'mark abc-123 as completed', '2026-01-27 10:05:00'),
('650e8400-e29b-41d4-a716-446655440001', 'assistant', '✅ Task marked as completed: "buy groceries"', '2026-01-27 10:05:01');
```

---

## Performance Considerations

### Query Optimization

1. **Conversation Context Loading** (most frequent query):
   ```sql
   -- Load last 10 messages for user
   SELECT * FROM messages
   WHERE conversation_id = (
       SELECT id FROM conversations WHERE user_id = $1 LIMIT 1
   )
   ORDER BY created_at DESC
   LIMIT 10;
   ```
   **Indexes Used**: `idx_messages_conversation_id`, `idx_messages_created_at`
   **Expected Performance**: <5ms

2. **Task Listing** (frequent):
   ```sql
   -- List all user tasks
   SELECT * FROM tasks
   WHERE user_id = $1
   ORDER BY created_at DESC;
   ```
   **Indexes Used**: `idx_tasks_user_id`
   **Expected Performance**: <10ms

3. **Fuzzy Task Search** (disambiguation):
   ```sql
   -- Find tasks matching search term
   SELECT * FROM tasks
   WHERE user_id = $1 AND title ILIKE '%' || $2 || '%'
   LIMIT 5;
   ```
   **Indexes Used**: `idx_tasks_user_id`
   **Expected Performance**: <15ms (no full-text search index needed for small datasets)

### Scalability

- **Conversation Growth**: 10 messages × 365 days = 3,650 messages/user/year (~1MB/user)
- **Task Growth**: 100 tasks/user (typical) × 500 bytes = 50KB/user
- **Database Size (1000 users, 1 year)**: ~1GB (manageable for SQLite)

**Future Optimization** (Phase IV+):
- Archive conversations older than 30 days
- Add full-text search index on `tasks.title` for faster fuzzy matching
- Migrate to PostgreSQL for production (>10k users)

---

## Data Model Status

✅ **Phase II Backward Compatibility**: All existing tables unchanged
✅ **Stateless Design**: Context reconstructed from DB (no in-memory state)
✅ **User Isolation**: All tables include `user_id` foreign key or relationship
✅ **Migration Path**: Clear SQL migrations defined
✅ **Performance**: Indexes optimized for query patterns

**Next Step**: Generate API contracts (Phase 1 continues)
