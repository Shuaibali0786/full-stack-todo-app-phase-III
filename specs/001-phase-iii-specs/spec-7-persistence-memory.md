# Feature Specification: Persistence & Memory for Conversational Todo Management

**Feature Branch**: `001-phase-iii-specs`
**Created**: 2026-01-25
**Status**: Draft
**Phase III Component**: Persistence & Memory Spec

## Constitutional Compliance

**Applicable Principles**:
- **Principle III (Stateless Architecture)**: NO in-memory state, conversation context reconstructed from database every request
- **Principle V (Clear Responsibility Separation)**: Database responsibility = persistent memory only, no business logic
- **Principle VI (Phase-II Protection)**: Only additive schema changes (new tables: conversations, messages), existing tables unchanged
- **Principle IX (Test-First Discipline)**: All database operations must be unit tested

**Database Context**:
- Phase-II Neon DB already provisioned (connection via `DATABASE_URL`)
- Phase-III adds TWO new tables: `conversations`, `messages`
- Existing tables (`tasks`, `users`, `auth`, `priorities`, `tags`) MUST remain unchanged
- All schema changes must be backward compatible

**MCP Role Declaration**:
- Database serves as persistent memory store only
- No business logic in schema (constraints enforce data integrity only)
- Conversation context reconstruction is read-only operation

---

## User Scenarios & Testing

### User Story 1 - Persist Conversation on First Message (Priority: P1)

System creates conversation record when user sends first message in a new session.

**Why this priority**: Foundation for all conversational features - must exist before messages can be stored.

**Independent Test**: Can be tested by POSTing first message to chat API and verifying `conversations` table has new row with user_id.

**Acceptance Scenarios**:

1. **Given** authenticated user sends first message, **When** chat API processes request, **Then** system creates conversation record with user_id, conversation_id (UUID), created_at timestamp

2. **Given** conversation already exists for user, **When** user sends another message, **Then** system reuses existing conversation (no duplicate conversations per user)

3. **Given** user is not authenticated, **When** message sent, **Then** system rejects request (no anonymous conversations)

---

### User Story 2 - Store Message in Conversation (Priority: P1)

System persists every user message and agent response to database.

**Why this priority**: Core requirement for context reconstruction - cannot be conversational without message history.

**Independent Test**: Can be tested by sending 3 messages in conversation and verifying `messages` table has 6 rows (3 user + 3 agent).

**Acceptance Scenarios**:

1. **Given** user sends message "add buy milk", **When** message processed, **Then** system stores user message with role='user', content='add buy milk', conversation_id, created_at

2. **Given** agent responds "✅ Created task: 'buy milk'", **When** response generated, **Then** system stores agent message with role='agent', content='✅ Created task...', conversation_id, created_at

3. **Given** messages stored, **When** queried by conversation_id, **Then** messages returned in chronological order (ORDER BY created_at ASC)

---

### User Story 3 - Reconstruct Context from Database (Priority: P1)

System retrieves conversation history from database on every request to provide context for agent reasoning.

**Why this priority**: Enables stateless architecture - must reconstruct context since no in-memory state allowed.

**Independent Test**: Can be tested by seeding database with 10 messages, restarting server, sending new message, and verifying agent has access to prior context.

**Acceptance Scenarios**:

1. **Given** conversation has 10 prior messages, **When** new message received, **Then** system retrieves last 50 messages from database (or all if <50) before invoking agent

2. **Given** retrieved context includes "user created task: buy milk", **When** user says "mark it done", **Then** agent can resolve "it" to "buy milk task" using context

3. **Given** conversation has 100 messages, **When** context reconstruction occurs, **Then** system retrieves only most recent 50 messages (performance constraint)

---

### User Story 4 - Resume Conversation After Server Restart (Priority: P2)

User can continue conversation after backend server restarts without losing context.

**Why this priority**: Critical for production reliability but depends on P1 (context reconstruction) being functional.

**Independent Test**: Can be tested by creating conversation, restarting FastAPI server, sending new message, and verifying agent responds with context from pre-restart messages.

**Acceptance Scenarios**:

1. **Given** conversation exists with 5 messages before server restart, **When** server restarts and user sends new message, **Then** agent retrieves 5 prior messages and responds with full context

2. **Given** no in-memory state persists after restart, **When** new request arrives, **Then** system reconstructs conversation_id from user_id (or session) and loads messages

3. **Given** database is source of truth, **When** server crashes mid-conversation, **Then** no messages are lost (all persisted before response sent)

---

### User Story 5 - Multi-Device Conversation Continuity (Priority: P3)

User can switch devices and continue same conversation (e.g., start on web, continue on mobile).

**Why this priority**: Nice-to-have for UX but not essential for MVP. Depends on session/authentication design.

**Independent Test**: Can be tested by authenticating same user on two different clients and verifying both see same conversation history.

**Acceptance Scenarios**:

1. **Given** user authenticated on Device A, **When** user authenticates on Device B, **Then** both devices retrieve same conversation_id and message history

2. **Given** user sends message from Device A, **When** Device B refreshes, **Then** Device B sees new message in conversation

3. **Given** multiple active sessions, **When** message sent from any session, **Then** all sessions share same conversation_id (one conversation per user)

---

### Edge Cases

- What happens when database is unavailable during message storage? → Request fails with error, user notified to retry (no partial conversations)
- How does system handle conversation_id collisions? → UUID collision is astronomically unlikely, but database unique constraint prevents duplicates
- What happens when message content exceeds max length? → Truncate with warning before storing (max 10,000 chars per message)
- How does system handle rapid-fire messages (burst of 10 messages in 1 second)? → Each message stored with unique ID and timestamp, processed sequentially
- What happens when conversation has 1000+ messages? → Context reconstruction limits to last 50 messages (older messages remain in database but not loaded into agent context)

---

## Requirements

### Functional Requirements

- **FR-001**: System MUST create `conversations` table with fields: id (UUID, PK), user_id (UUID, FK to users.id), created_at (timestamp), updated_at (timestamp)
- **FR-002**: System MUST create `messages` table with fields: id (UUID, PK), conversation_id (UUID, FK to conversations.id), role (enum: 'user' | 'agent'), content (text), created_at (timestamp)
- **FR-003**: System MUST create conversation record on first message from user (if no conversation exists for user_id)
- **FR-004**: System MUST store user messages with role='user' immediately upon receipt
- **FR-005**: System MUST store agent responses with role='agent' after generation
- **FR-006**: System MUST retrieve conversation messages in chronological order (ORDER BY created_at ASC)
- **FR-007**: System MUST limit context reconstruction to most recent 50 messages per conversation (performance constraint)
- **FR-008**: System MUST reconstruct conversation context from database on every request (no in-memory caching between requests)
- **FR-009**: System MUST associate conversations with authenticated user (user_id foreign key)
- **FR-010**: System MUST prevent cross-user conversation access (WHERE user_id = authenticated_user_id)
- **FR-011**: System MUST persist messages atomically (transaction wraps user message storage + agent response storage)
- **FR-012**: System MUST NOT modify existing Phase-II tables (tasks, users, auth, priorities, tags)
- **FR-013**: System MUST support conversation continuation after server restart (database is source of truth)
- **FR-014**: System MUST truncate messages exceeding 10,000 characters before storage
- **FR-015**: System MUST index conversations by user_id for fast lookup
- **FR-016**: System MUST index messages by conversation_id for fast retrieval

### Key Entities

- **Conversation**: Represents a chat session between user and agent
  - Attributes: id (UUID), user_id (UUID), created_at (timestamp), updated_at (timestamp)
  - Relationships: belongs_to User (via user_id), has_many Messages
  - Constraints: Unique per user (one active conversation per user)

- **Message**: Represents a single message in conversation (user input or agent response)
  - Attributes: id (UUID), conversation_id (UUID), role ('user' | 'agent'), content (text, max 10,000 chars), created_at (timestamp)
  - Relationships: belongs_to Conversation (via conversation_id)
  - Constraints: NOT NULL on conversation_id, role, content

- **ConversationContext**: In-memory representation of conversation history (reconstructed from database)
  - Attributes: conversation_id (UUID), messages (array of Message objects, max 50)
  - Lifecycle: Loaded from database at request start, discarded at request end (stateless)

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: System stores 100% of user messages and agent responses (no message loss)
- **SC-002**: Conversation context reconstruction completes in under 500ms for 50-message conversations
- **SC-003**: System handles server restart without losing any persisted messages (database verification)
- **SC-004**: Zero in-memory conversation state persists between requests (stateless validation)
- **SC-005**: Context reconstruction query uses index (query plan shows index scan, not table scan)
- **SC-006**: System prevents cross-user conversation access (authorization test with 2 users)
- **SC-007**: Message storage transaction succeeds or fails atomically (no partial conversations)
- **SC-008**: System handles 1000 concurrent conversation reconstructions without performance degradation
- **SC-009**: Database schema migration completes without downtime for existing Phase-II functionality
- **SC-010**: Conversation history available across multiple user sessions/devices (same user sees same messages)

---

## Database Schema Design

### Table: conversations

**Purpose**: Store metadata for user conversations.

**Schema**:
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(user_id)  -- One conversation per user
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
```

**Design Rationale**:
- `id`: UUID for distributed systems compatibility, serves as conversation identifier
- `user_id`: Foreign key to existing users table, enables user-specific conversations
- `UNIQUE(user_id)`: Enforces one conversation per user (Phase III MVP constraint)
- `ON DELETE CASCADE`: When user deleted, conversation automatically deleted
- `created_at`/`updated_at`: Audit timestamps

**Constraints**:
- Primary Key: `id`
- Foreign Key: `user_id` → `users.id`
- Unique: `user_id`
- NOT NULL: `id`, `user_id`, `created_at`, `updated_at`

---

### Table: messages

**Purpose**: Store individual messages in conversations.

**Schema**:
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(10) NOT NULL CHECK (role IN ('user', 'agent')),
    content TEXT NOT NULL CHECK (LENGTH(content) <= 10000),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(conversation_id, created_at);
```

**Design Rationale**:
- `id`: UUID for message identifier
- `conversation_id`: Foreign key to conversations, groups messages by conversation
- `role`: Enum-like field distinguishing user vs agent messages (stored as VARCHAR with CHECK constraint)
- `content`: TEXT field supporting up to 10,000 characters (CHECK constraint enforces limit)
- `created_at`: Timestamp for chronological ordering
- `ON DELETE CASCADE`: When conversation deleted, all messages automatically deleted
- Indexes: Fast retrieval by conversation_id, fast chronological ordering

**Constraints**:
- Primary Key: `id`
- Foreign Key: `conversation_id` → `conversations.id`
- CHECK: `role IN ('user', 'agent')`
- CHECK: `LENGTH(content) <= 10000`
- NOT NULL: `id`, `conversation_id`, `role`, `content`, `created_at`

---

## Data Flow Specifications

### Flow 1: First Message in New Conversation

**Steps**:
1. User sends message to chat API
2. API validates authentication (extracts user_id from session/token)
3. API queries: `SELECT id FROM conversations WHERE user_id = ?`
4. If no conversation exists:
   - API inserts: `INSERT INTO conversations (user_id) VALUES (?) RETURNING id`
5. API inserts user message: `INSERT INTO messages (conversation_id, role, content) VALUES (?, 'user', ?)`
6. Agent processes message (with empty context, since first message)
7. API inserts agent response: `INSERT INTO messages (conversation_id, role, content) VALUES (?, 'agent', ?)`
8. API returns agent response to user

**Transaction Boundary**: Steps 5-7 wrapped in single transaction (atomic message storage)

---

### Flow 2: Subsequent Message in Existing Conversation

**Steps**:
1. User sends message to chat API
2. API validates authentication (extracts user_id)
3. API queries: `SELECT id FROM conversations WHERE user_id = ?` (finds existing conversation)
4. API reconstructs context: `SELECT role, content, created_at FROM messages WHERE conversation_id = ? ORDER BY created_at DESC LIMIT 50`
5. API inserts user message: `INSERT INTO messages (conversation_id, role, content) VALUES (?, 'user', ?)`
6. Agent processes message (with reconstructed context)
7. API inserts agent response: `INSERT INTO messages (conversation_id, role, content) VALUES (?, 'agent', ?)`
8. API returns agent response to user

**Transaction Boundary**: Steps 5-7 wrapped in single transaction

---

### Flow 3: Context Reconstruction on Every Request

**Purpose**: Load conversation history from database to provide agent with context (stateless operation).

**Query**:
```sql
SELECT role, content, created_at
FROM messages
WHERE conversation_id = ?
ORDER BY created_at DESC
LIMIT 50
```

**Performance Optimization**:
- Query uses `idx_messages_created_at` index (fast retrieval)
- Limit 50 messages prevents loading excessive data
- Result reversed to chronological order (oldest first) before passing to agent

**Caching Policy**: NO caching (stateless requirement) - context reconstructed from database on every request

---

## Migration Strategy

### Migration Plan

**Objective**: Add `conversations` and `messages` tables without disrupting Phase-II functionality.

**Steps**:

1. **Create Migration File**: `migrations/add_conversations_tables.sql`

```sql
-- Migration: Add Phase III conversation tables
-- Date: 2026-01-25
-- Description: Add conversations and messages tables for AI chat feature

BEGIN;

CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(user_id)
);

CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(10) NOT NULL CHECK (role IN ('user', 'agent')),
    content TEXT NOT NULL CHECK (LENGTH(content) <= 10000),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(conversation_id, created_at);

COMMIT;
```

2. **Test Migration on Staging**: Run migration on staging database, verify no Phase-II functionality broken

3. **Deploy Migration**: Apply migration to production database

4. **Rollback Plan**: Drop tables if needed:
```sql
DROP TABLE IF EXISTS messages CASCADE;
DROP TABLE IF EXISTS conversations CASCADE;
```

**Backward Compatibility**:
- New tables do not affect existing Phase-II queries
- No foreign keys from existing tables to new tables
- No triggers or constraints on existing tables

---

## Performance Requirements

### Query Performance Targets

| Operation | Target Latency | Index Used | Notes |
|-----------|---------------|------------|-------|
| Find conversation by user_id | < 10ms | idx_conversations_user_id | Lookup for every request |
| Retrieve last 50 messages | < 100ms | idx_messages_created_at | Context reconstruction |
| Insert message | < 50ms | N/A | Transactional write |
| Create conversation | < 50ms | N/A | Rare operation (once per user) |

### Scalability Constraints

- **Max Messages Per Conversation**: Unlimited (but only last 50 loaded into context)
- **Max Conversations Per User**: 1 (Phase III MVP constraint, enforced by UNIQUE constraint)
- **Max Message Length**: 10,000 characters (enforced by CHECK constraint)
- **Concurrent Conversations**: Supports 1000+ concurrent users (database connection pool handles concurrency)

### Database Connection Pool

- Reuse existing Phase-II connection pool (no additional connections)
- Max connections: 20 (typical for Neon Serverless PostgreSQL)
- Connection timeout: 30 seconds

---

## Security Requirements

### Data Access Control

- **Authorization**: Users can ONLY access their own conversations (WHERE user_id = authenticated_user_id)
- **Isolation**: No user can read another user's messages (enforced by application logic + foreign key constraints)
- **Authentication**: All database operations require authenticated user_id (no anonymous conversations)

### Data Privacy

- **Message Content**: May contain sensitive information (PII, personal todos), must be treated as confidential
- **Logging**: Do NOT log full message content in application logs (log metadata only: conversation_id, message_id, role, timestamp)
- **Encryption**: Database connection uses TLS (Neon default), messages encrypted at rest by database provider

### Injection Prevention

- **SQL Injection**: Use parameterized queries (SQLModel handles this automatically)
- **Content Sanitization**: No HTML/script tags allowed in message content (sanitized before storage)

---

## Testing Strategy

### Unit Tests

**conversations table**:
- Create conversation for new user → success
- Create duplicate conversation for same user → constraint violation
- Query conversation by user_id → returns correct conversation
- Delete conversation → cascades to messages

**messages table**:
- Insert user message → success
- Insert agent message → success
- Insert message with invalid role → constraint violation
- Insert message exceeding 10,000 chars → constraint violation
- Query messages by conversation_id → returns in chronological order
- Retrieve last 50 messages → returns correct subset

### Integration Tests

- Full flow: Create conversation → Store user message → Store agent response → Retrieve context
- Server restart: Create conversation → Restart server → Retrieve context (verify persistence)
- Concurrent writes: 10 users send messages simultaneously (verify no race conditions)

### Performance Tests

- Context reconstruction for 50-message conversation (target < 100ms)
- 1000 concurrent conversation reconstructions (verify no degradation)
- Query plan analysis (verify indexes used)

---

## Assumptions

1. One conversation per user (Phase III MVP constraint, may be relaxed in future)
2. Last 50 messages sufficient for context (performance vs completeness tradeoff)
3. Message content primarily text (no file attachments, images, or rich media)
4. Users access conversations sequentially (not editing past messages)
5. Conversation deletion handled by user account deletion (no separate "delete conversation" feature)
6. All timestamps in UTC (timezone conversion handled by client)

---

## Out of Scope for Phase III

- Multiple conversations per user (thread management)
- Message editing or deletion by users
- Conversation search or filtering
- Message attachments (files, images)
- Conversation export (download history as JSON/CSV)
- Conversation sharing between users
- Soft deletes (messages/conversations are hard deleted)

---

## Dependencies

**Phase II Components** (must remain functional):
- Database schema: `users` table (foreign key target for conversations.user_id)
- Authentication: Provides user_id for conversation association
- Database connection pool: Reused for new tables

**Phase III Components** (dependencies for this spec):
- Agent Behavior Spec (spec-5): Consumes reconstructed context
- MCP Server Spec (spec-6): May need conversation_id for audit logging
- Chat API: Orchestrates conversation creation, message storage, context reconstruction

**External Services**:
- Neon Serverless PostgreSQL: Hosts new tables

---

## Acceptance Criteria

**This specification is ready for planning when**:

1. Database schema for both tables is complete with all constraints
2. Migration strategy defined with rollback plan
3. Data flow specifications cover all conversation scenarios
4. Performance targets defined with index strategy
5. Security requirements explicit (authorization, privacy, injection prevention)
6. Testing strategy covers unit, integration, and performance tests
7. No [NEEDS CLARIFICATION] markers remain
8. Success criteria are measurable and verifiable
9. Phase-II protection requirements documented (no existing table modifications)

**Planning phase should validate**:

1. SQLModel supports new table schemas (UUID, CHECK constraints, timestamps)
2. Database migration can be applied without downtime
3. Index strategy supports performance targets (query plan analysis)
4. One-conversation-per-user constraint acceptable for MVP (or needs revision)
