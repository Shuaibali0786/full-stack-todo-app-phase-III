# Feature Specification: MCP Server for Todo Task Management

**Feature Branch**: `001-phase-iii-specs`
**Created**: 2026-01-25
**Status**: Draft
**Phase III Component**: MCP Server Spec

## Constitutional Compliance

**Applicable Principles**:
- **Principle III (Stateless Architecture)**: MCP tools MUST be stateless, no in-memory state
- **Principle IV (Tool-Only Mutation Rule)**: MCP tools are the ONLY path for database mutations
- **Principle V (Clear Responsibility Separation)**: MCP tools responsibility = pure data operations, no AI reasoning
- **Principle VI (Phase-II Protection)**: MCP tools extend but do not replace Phase-II APIs
- **Principle IX (Test-First Discipline)**: 100% test coverage required for all MCP tools

**Database Context**:
- Phase-II Neon DB already provisioned (connection via `DATABASE_URL`)
- MCP tools operate on existing tables: `tasks`, `users`
- MCP tools must NOT modify existing table schemas
- All operations must respect user authentication/authorization

**MCP Role Declaration**:
- MCP server provides stateless, database-backed tools only
- No business logic, no AI reasoning, no validation beyond data integrity
- All changes must be traceable and atomic

---

## User Scenarios & Testing

### User Story 1 - Add Task Tool (Priority: P1)

MCP tool accepts task parameters and persists new task to database.

**Why this priority**: Core mutation operation required for conversational task creation.

**Independent Test**: Can be tested by calling `add_task` tool directly with test parameters and verifying task appears in database.

**Acceptance Scenarios**:

1. **Given** valid task parameters (title="buy milk", user_id=123, due_date="2026-01-30"), **When** `add_task` tool is invoked, **Then** tool creates task in database, returns task_id and full task object

2. **Given** minimal task parameters (title only), **When** `add_task` tool is invoked, **Then** tool creates task with defaults (is_completed=false, no due_date), returns created task

3. **Given** invalid parameters (missing title), **When** `add_task` tool is invoked, **Then** tool returns error with clear message "title is required"

---

### User Story 2 - List Tasks Tool (Priority: P1)

MCP tool queries database and returns filtered task list.

**Why this priority**: Core read operation required for displaying tasks to users.

**Independent Test**: Can be tested by seeding database with tasks, calling `list_tasks` with filters, and verifying correct tasks returned.

**Acceptance Scenarios**:

1. **Given** user has 5 tasks (2 completed, 3 pending), **When** `list_tasks` tool is invoked with no filters, **Then** tool returns all 5 tasks

2. **Given** `list_tasks` tool is invoked with filter completed=false, **When** query executes, **Then** tool returns only the 3 pending tasks

3. **Given** `list_tasks` tool is invoked with filter due_date="2026-01-30", **When** query executes, **Then** tool returns only tasks due on that date

---

### User Story 3 - Update Task Tool (Priority: P1)

MCP tool updates existing task fields.

**Why this priority**: Core mutation operation required for task modifications.

**Independent Test**: Can be tested by creating a task, calling `update_task` with new values, and verifying database reflects changes.

**Acceptance Scenarios**:

1. **Given** task exists with id=123, **When** `update_task` tool is invoked with new title="buy almond milk", **Then** tool updates task, returns updated task object

2. **Given** task exists, **When** `update_task` tool is invoked with partial update (only due_date), **Then** tool updates only due_date field, other fields unchanged

3. **Given** task does not exist (id=999), **When** `update_task` tool is invoked, **Then** tool returns error "task not found"

---

### User Story 4 - Complete Task Tool (Priority: P2)

MCP tool marks task as completed.

**Why this priority**: Common operation but can be implemented via `update_task` as fallback.

**Independent Test**: Can be tested by creating pending task, calling `complete_task`, and verifying is_completed=true.

**Acceptance Scenarios**:

1. **Given** task exists with is_completed=false, **When** `complete_task` tool is invoked, **Then** tool sets is_completed=true, updates updated_at timestamp

2. **Given** task already completed, **When** `complete_task` tool is invoked again, **Then** tool succeeds idempotently (no error)

3. **Given** task does not exist, **When** `complete_task` tool is invoked, **Then** tool returns error "task not found"

---

### User Story 5 - Delete Task Tool (Priority: P2)

MCP tool permanently removes task from database.

**Why this priority**: Less common operation (users typically complete rather than delete).

**Independent Test**: Can be tested by creating task, calling `delete_task`, and verifying task no longer exists in database.

**Acceptance Scenarios**:

1. **Given** task exists with id=123, **When** `delete_task` tool is invoked, **Then** tool deletes task from database, returns success confirmation

2. **Given** task does not exist, **When** `delete_task` tool is invoked, **Then** tool returns error "task not found"

3. **Given** task has related data (tags, recurring instances), **When** `delete_task` tool is invoked, **Then** tool cascades delete or returns error based on database constraints

---

### Edge Cases

- What happens when database connection fails during tool execution? → Tool returns error, does not crash, does not retry automatically
- How does tool handle concurrent updates to same task? → Tool relies on database row locking, last write wins
- What happens when user_id is invalid (user does not exist)? → Tool returns error "user not found" or "unauthorized"
- How does tool handle malformed UUIDs? → Tool validates UUID format, returns error "invalid ID format"
- What happens when database transaction fails mid-operation? → Tool rolls back transaction, returns error, no partial writes

---

## Requirements

### Functional Requirements

- **FR-001**: MCP server MUST implement `add_task` tool accepting parameters: title (string, required), description (string, optional), user_id (UUID, required), due_date (datetime, optional), reminder_time (datetime, optional), priority_id (UUID, optional)
- **FR-002**: MCP server MUST implement `list_tasks` tool accepting parameters: user_id (UUID, required), completed (bool, optional), due_date (datetime, optional), priority_id (UUID, optional), tag_id (UUID, optional), limit (int, optional, default=50), offset (int, optional, default=0)
- **FR-003**: MCP server MUST implement `update_task` tool accepting parameters: task_id (UUID, required), user_id (UUID, required), title (string, optional), description (string, optional), due_date (datetime, optional), reminder_time (datetime, optional), is_completed (bool, optional), priority_id (UUID, optional)
- **FR-004**: MCP server MUST implement `complete_task` tool accepting parameters: task_id (UUID, required), user_id (UUID, required)
- **FR-005**: MCP server MUST implement `delete_task` tool accepting parameters: task_id (UUID, required), user_id (UUID, required)
- **FR-006**: All MCP tools MUST validate user_id matches task owner (authorization check)
- **FR-007**: All MCP tools MUST use database transactions (atomic operations, rollback on failure)
- **FR-008**: All MCP tools MUST be stateless (no in-memory caching, no session state)
- **FR-009**: All MCP tools MUST return standardized error responses (error_code, error_message)
- **FR-010**: All MCP tools MUST log operations for audit trail (user_id, operation, timestamp, success/failure)
- **FR-011**: MCP tools MUST NOT modify existing Phase-II database schema
- **FR-012**: MCP tools MUST use existing Phase-II database connection pool (no separate connections)
- **FR-013**: MCP tools MUST validate input schemas before database operations
- **FR-014**: MCP tools MUST return complete task objects including all fields (id, title, description, is_completed, user_id, due_date, reminder_time, created_at, updated_at, priority_id)
- **FR-015**: MCP server MUST expose tools via official MCP SDK protocol (tool discovery, invocation, error handling)

### Key Entities

- **MCPTool**: Callable function exposed via MCP protocol
  - Attributes: tool_name, input_schema, output_schema, description
  - Operations: validate_input, execute, handle_error

- **TaskInput**: Input parameters for task operations
  - Attributes: task_id (UUID), title (string), description (string), due_date (datetime), reminder_time (datetime), is_completed (bool), user_id (UUID), priority_id (UUID)
  - Validation: Required vs optional fields per tool

- **TaskOutput**: Response from task operations
  - Attributes: task object (full model) or error object (error_code, error_message)
  - Format: JSON-serializable

- **DatabaseConnection**: Stateless connection to Neon PostgreSQL
  - Attributes: connection_string (from DATABASE_URL), connection_pool
  - Lifecycle: Connection per request, no persistent state

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: All 5 MCP tools execute successfully for valid inputs (100% success rate in tests)
- **SC-002**: MCP tools respond within 200ms for 95% of operations (database latency included)
- **SC-003**: MCP tools handle 1000 concurrent requests without errors (stateless validation)
- **SC-004**: Zero database writes occur outside of MCP tool execution (audit log verification)
- **SC-005**: MCP tools have 100% unit test coverage (all CRUD operations)
- **SC-006**: MCP tools correctly rollback transactions on failure (no partial writes)
- **SC-007**: MCP tools validate all inputs before database operations (no SQL injection vulnerabilities)
- **SC-008**: MCP server survives database connection failures without crashing (graceful error handling)
- **SC-009**: MCP tools return standardized errors with user-friendly messages (no stack traces exposed)
- **SC-010**: All MCP tool operations are logged with audit trail (user_id, operation, timestamp, result)

---

## MCP Tool Specifications

### Tool 1: add_task

**Purpose**: Create a new task for a user.

**Input Schema** (JSON):
```json
{
  "title": "string (required, max 255 chars)",
  "description": "string (optional, max 5000 chars)",
  "user_id": "UUID (required)",
  "due_date": "ISO8601 datetime (optional)",
  "reminder_time": "ISO8601 datetime (optional)",
  "priority_id": "UUID (optional)"
}
```

**Output Schema** (JSON):
```json
{
  "id": "UUID",
  "title": "string",
  "description": "string | null",
  "is_completed": false,
  "user_id": "UUID",
  "due_date": "ISO8601 datetime | null",
  "reminder_time": "ISO8601 datetime | null",
  "priority_id": "UUID | null",
  "created_at": "ISO8601 datetime",
  "updated_at": "ISO8601 datetime"
}
```

**Error Conditions**:
- `VALIDATION_ERROR`: Missing title or invalid user_id
- `DATABASE_ERROR`: Database connection failure or constraint violation
- `UNAUTHORIZED`: user_id does not exist

**Database Operations**:
1. Validate user_id exists in `users` table
2. Insert new row into `tasks` table
3. Return created task object

---

### Tool 2: list_tasks

**Purpose**: Retrieve tasks for a user with optional filters.

**Input Schema** (JSON):
```json
{
  "user_id": "UUID (required)",
  "completed": "boolean (optional)",
  "due_date": "ISO8601 date (optional, matches tasks due on this date)",
  "priority_id": "UUID (optional)",
  "tag_id": "UUID (optional)",
  "limit": "integer (optional, default=50, max=200)",
  "offset": "integer (optional, default=0)"
}
```

**Output Schema** (JSON):
```json
{
  "tasks": [
    {
      "id": "UUID",
      "title": "string",
      "description": "string | null",
      "is_completed": "boolean",
      "user_id": "UUID",
      "due_date": "ISO8601 datetime | null",
      "reminder_time": "ISO8601 datetime | null",
      "priority_id": "UUID | null",
      "created_at": "ISO8601 datetime",
      "updated_at": "ISO8601 datetime"
    }
  ],
  "total": "integer (total matching tasks before limit/offset)",
  "limit": "integer",
  "offset": "integer"
}
```

**Error Conditions**:
- `VALIDATION_ERROR`: Invalid user_id or filter parameters
- `DATABASE_ERROR`: Database connection failure

**Database Operations**:
1. Validate user_id exists
2. Query `tasks` table with filters (WHERE user_id=X AND completed=Y AND ...)
3. Apply limit/offset for pagination
4. Return task array and total count

---

### Tool 3: update_task

**Purpose**: Update existing task fields.

**Input Schema** (JSON):
```json
{
  "task_id": "UUID (required)",
  "user_id": "UUID (required)",
  "title": "string (optional, max 255 chars)",
  "description": "string (optional, max 5000 chars)",
  "due_date": "ISO8601 datetime (optional)",
  "reminder_time": "ISO8601 datetime (optional)",
  "is_completed": "boolean (optional)",
  "priority_id": "UUID (optional)"
}
```

**Output Schema** (JSON):
```json
{
  "id": "UUID",
  "title": "string",
  "description": "string | null",
  "is_completed": "boolean",
  "user_id": "UUID",
  "due_date": "ISO8601 datetime | null",
  "reminder_time": "ISO8601 datetime | null",
  "priority_id": "UUID | null",
  "created_at": "ISO8601 datetime",
  "updated_at": "ISO8601 datetime"
}
```

**Error Conditions**:
- `NOT_FOUND`: task_id does not exist
- `UNAUTHORIZED`: task does not belong to user_id
- `VALIDATION_ERROR`: Invalid field values
- `DATABASE_ERROR`: Database connection failure

**Database Operations**:
1. Validate task exists and belongs to user_id
2. Update only provided fields (partial update)
3. Update `updated_at` timestamp
4. Return updated task object

---

### Tool 4: complete_task

**Purpose**: Mark task as completed (shorthand for update_task with is_completed=true).

**Input Schema** (JSON):
```json
{
  "task_id": "UUID (required)",
  "user_id": "UUID (required)"
}
```

**Output Schema** (JSON):
```json
{
  "id": "UUID",
  "title": "string",
  "description": "string | null",
  "is_completed": true,
  "user_id": "UUID",
  "due_date": "ISO8601 datetime | null",
  "reminder_time": "ISO8601 datetime | null",
  "priority_id": "UUID | null",
  "created_at": "ISO8601 datetime",
  "updated_at": "ISO8601 datetime"
}
```

**Error Conditions**:
- `NOT_FOUND`: task_id does not exist
- `UNAUTHORIZED`: task does not belong to user_id
- `DATABASE_ERROR`: Database connection failure

**Database Operations**:
1. Validate task exists and belongs to user_id
2. Update is_completed=true
3. Update `updated_at` timestamp
4. Return updated task object

**Note**: Idempotent operation (calling on already-completed task succeeds)

---

### Tool 5: delete_task

**Purpose**: Permanently remove task from database.

**Input Schema** (JSON):
```json
{
  "task_id": "UUID (required)",
  "user_id": "UUID (required)"
}
```

**Output Schema** (JSON):
```json
{
  "success": true,
  "message": "Task deleted successfully"
}
```

**Error Conditions**:
- `NOT_FOUND`: task_id does not exist
- `UNAUTHORIZED`: task does not belong to user_id
- `DATABASE_ERROR`: Database connection failure or constraint violation

**Database Operations**:
1. Validate task exists and belongs to user_id
2. Delete row from `tasks` table
3. Return success confirmation

**Note**: Cascading deletes for related data (task_tags) handled by database foreign key constraints

---

## Error Handling Specifications

### Standardized Error Response Format

All MCP tools MUST return errors in this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "User-friendly error message",
    "details": {
      "field": "field_name (for validation errors)",
      "timestamp": "ISO8601 datetime"
    }
  }
}
```

### Error Codes

| Code | Description | User-Facing Message | HTTP Status Equivalent |
|------|-------------|---------------------|----------------------|
| `VALIDATION_ERROR` | Invalid input parameters | "Invalid input: [field] is required" | 400 |
| `NOT_FOUND` | Task or user does not exist | "Task not found" | 404 |
| `UNAUTHORIZED` | User does not own task | "You don't have permission to modify this task" | 403 |
| `DATABASE_ERROR` | Database connection or query failure | "Unable to save changes. Please try again." | 500 |
| `CONSTRAINT_VIOLATION` | Foreign key or unique constraint violated | "Invalid reference: [entity] does not exist" | 400 |

### Error Handling Best Practices

1. **Do NOT expose internal errors**: Never return stack traces, SQL errors, or connection strings
2. **Log all errors**: Include user_id, operation, timestamp, error details in logs
3. **Rollback transactions**: Ensure database remains consistent on failure
4. **Return quickly**: Do not retry failed operations automatically (let caller decide)
5. **Validate early**: Check input parameters before database operations

---

## Database Integration

### Connection Management

- **Connection String**: Retrieved from environment variable `DATABASE_URL`
- **Connection Pool**: Use SQLModel's async connection pool (shared with Phase-II)
- **Connection Lifecycle**: Open connection per request, close after operation completes
- **No Persistent State**: MCP tools must NOT cache database connections or query results

### Transaction Requirements

All write operations (add, update, delete) MUST use transactions:

```python
async with session.begin():
    # Perform database operations
    # If any operation fails, transaction rolls back automatically
```

### Schema Constraints

MCP tools MUST respect existing database constraints:

- **Foreign Keys**: `user_id` references `users.id`, `priority_id` references `priorities.id`
- **Unique Constraints**: None on tasks table
- **Not Null**: `title`, `user_id`, `is_completed` must always have values
- **Defaults**: `is_completed` defaults to `false`, timestamps default to current time

### Query Optimization

- Use indexed columns for filtering (user_id, is_completed, due_date)
- Limit result sets (default limit=50, max=200)
- Avoid SELECT * (specify required columns)

---

## Security Requirements

### Authentication

- MCP tools MUST validate user_id corresponds to authenticated user
- MCP tools MUST NOT allow cross-user data access
- MCP tools MUST NOT expose other users' task data

### Authorization

- User can only read/write their own tasks (WHERE user_id = authenticated_user_id)
- Admin users (if implemented) can access all tasks (out of scope for Phase III MVP)

### Input Validation

- Sanitize all string inputs (prevent SQL injection, XSS)
- Validate UUID formats before queries
- Validate date/time formats (ISO8601 only)
- Enforce max lengths (title: 255 chars, description: 5000 chars)

### Data Protection

- Do NOT log sensitive data (task descriptions may contain personal info)
- Use parameterized queries (SQLModel handles this automatically)
- Do NOT store plaintext passwords (handled by Phase-II auth, out of scope here)

---

## Testing Strategy

### Unit Tests (100% Coverage Required)

**add_task**:
- Valid input → task created
- Missing title → validation error
- Invalid user_id → unauthorized error
- Database failure → database error

**list_tasks**:
- No filters → all user tasks returned
- Filter by completed=true → only completed tasks
- Filter by due_date → only tasks due on date
- Pagination (limit/offset) → correct subset returned

**update_task**:
- Partial update (title only) → only title changed
- Update non-existent task → not found error
- Update other user's task → unauthorized error

**complete_task**:
- Complete pending task → is_completed=true
- Complete already-completed task → idempotent success
- Complete non-existent task → not found error

**delete_task**:
- Delete existing task → success
- Delete non-existent task → not found error
- Delete other user's task → unauthorized error

### Integration Tests

- MCP server → Database → MCP server (full round-trip)
- Concurrent tool calls (stateless validation)
- Database transaction rollback on error

### Performance Tests

- 1000 concurrent `list_tasks` calls (stateless validation)
- Response time under 200ms for 95% of operations
- Connection pool exhaustion handling

---

## Assumptions

1. MCP tools operate in same process as FastAPI server (no separate MCP server deployment)
2. Database connection pool is shared with Phase-II (no additional connections needed)
3. MCP SDK handles tool discovery and invocation protocol (no custom protocol implementation)
4. User authentication already handled by FastAPI middleware (MCP tools receive authenticated user_id)
5. Database schema migrations handled separately (MCP tools do not modify schema)
6. All datetime values stored in UTC (timezone conversion handled by client)

---

## Out of Scope for Phase III

- Batch operations (create/update/delete multiple tasks in one call)
- Task sharing/collaboration features
- Advanced filtering (full-text search, date ranges, sorting)
- Soft deletes (tasks are permanently deleted, no recycle bin)
- Task history/audit log (beyond basic operation logging)
- File attachments or rich media

---

## Dependencies

**Phase II Components** (must remain functional):
- Database schema (`tasks`, `users`, `priorities`, `tags` tables)
- Database connection pool (SQLModel AsyncSession)
- User authentication (Better Auth provides user_id)

**Phase III Components** (dependencies for this spec):
- Agent Behavior Spec (spec-5): Consumes MCP tools defined here
- Persistence & Memory Spec (spec-7): May add conversation-related tables

**External Services**:
- Neon Serverless PostgreSQL: Database hosting
- Official MCP SDK (Python): Tool registration and invocation protocol

---

## Acceptance Criteria

**This specification is ready for planning when**:

1. All 5 MCP tools have complete input/output schemas
2. All error conditions are documented with standardized responses
3. Database operations are specified for each tool (queries, transactions)
4. Security requirements are explicit (authentication, authorization, input validation)
5. Testing strategy covers unit, integration, and performance tests
6. No [NEEDS CLARIFICATION] markers remain
7. Success criteria are measurable and technology-agnostic
8. Phase-II protection requirements are documented

**Planning phase should validate**:

1. Official MCP SDK supports all required tool features
2. SQLModel async operations support transactional writes
3. Database schema supports all required queries (indexes, constraints)
4. Performance targets achievable with Neon Serverless PostgreSQL latency
