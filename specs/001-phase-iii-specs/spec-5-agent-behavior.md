# Feature Specification: Agent Behavior for Conversational Todo Management

**Feature Branch**: `001-phase-iii-specs`
**Created**: 2026-01-25
**Status**: Draft
**Phase III Component**: Agent Behavior Spec

## Constitutional Compliance

**Applicable Principles**:
- **Principle II (Spec-Driven Authority)**: This spec defines authoritative agent behavior
- **Principle IV (Tool-Only Mutation Rule)**: Agent MUST NOT write to database directly
- **Principle V (Clear Responsibility Separation)**: Agent responsibility = NLU + intent detection + reasoning
- **Principle VI (Phase-II Protection)**: Agent extends but does not replace Phase-II functionality
- **Principle VIII (Agent Behavior Standards)**: Transparency, confirmation, graceful errors mandatory

**Database Context**:
- Phase-II Neon DB already provisioned (connection via `DATABASE_URL`)
- Agent may READ from database for context reconstruction
- Agent MUST use MCP tools for ALL mutations (no direct writes)
- Existing tables (`tasks`, `users`, `auth`) remain unchanged

**MCP Role Declaration**:
- Agent operates as MCP-compliant: all database mutations via MCP tools only
- Agent may only extend existing behavior, not replace it
- All changes must be traceable and spec-driven

---

## User Scenarios & Testing

### User Story 1 - Create Task via Natural Language (Priority: P1)

User speaks naturally to create a todo task without needing to know API schemas or fill forms.

**Why this priority**: Core value proposition of Phase III - natural language interaction is the primary differentiator from Phase II.

**Independent Test**: Can be fully tested by sending "add buy milk to my tasks" and verifying task appears in database via Phase II APIs.

**Acceptance Scenarios**:

1. **Given** user is authenticated and has an active conversation, **When** user says "remind me to buy milk tomorrow at 3pm", **Then** agent detects CREATE intent, extracts title/due_date/reminder, calls `add_task` MCP tool, and confirms "✅ Created task: 'buy milk' (due tomorrow at 3pm)"

2. **Given** user says "add call dentist", **When** no due date or reminder specified, **Then** agent creates task with title only and confirms "✅ Created task: 'call dentist'"

3. **Given** user says "new task: finish report by Friday", **When** intent includes relative date, **Then** agent resolves "Friday" to absolute date and creates task with correct due_date

---

### User Story 2 - List and Query Tasks (Priority: P1)

User queries their tasks in natural language to see what needs to be done.

**Why this priority**: Essential for usability - users need to retrieve information as easily as they create it.

**Independent Test**: Can be tested by creating tasks via Phase II API, then asking "what's on my list?" and verifying agent returns correct tasks.

**Acceptance Scenarios**:

1. **Given** user has 5 tasks (2 completed, 3 pending), **When** user asks "show me my tasks", **Then** agent calls `list_tasks` with no filters and displays all tasks in natural language format

2. **Given** user asks "what do I need to do today?", **When** query implies filtering by due date, **Then** agent calls `list_tasks` with date filter and returns only today's tasks

3. **Given** user has no tasks, **When** user asks "what's next?", **Then** agent responds "You're all caught up! No pending tasks."

---

### User Story 3 - Update Task via Natural Language (Priority: P2)

User modifies existing tasks through conversational commands.

**Why this priority**: Important for task management workflows but depends on P1 (create/list) being functional.

**Independent Test**: Can be tested by creating a task, then saying "change the milk task to tomorrow" and verifying update persisted.

**Acceptance Scenarios**:

1. **Given** user has task "buy milk" with ID=123, **When** user says "move the milk task to tomorrow", **Then** agent identifies task by title, calls `update_task` with new due_date, confirms "✅ Updated 'buy milk' - now due tomorrow"

2. **Given** user says "mark buy milk as done", **When** intent is COMPLETE, **Then** agent calls `complete_task` with task ID, confirms "✅ Completed 'buy milk'"

3. **Given** user says "update task" without specifying which task, **When** intent is ambiguous, **Then** agent requests clarification: "❓ Which task would you like to update? You have: [list of tasks]"

---

### User Story 4 - Delete Task via Natural Language (Priority: P2)

User removes tasks they no longer need.

**Why this priority**: Standard CRUD operation, but lower priority than create/read/update as users typically complete rather than delete.

**Independent Test**: Can be tested by creating a task, then saying "delete the milk task" and verifying it's removed.

**Acceptance Scenarios**:

1. **Given** user says "delete buy milk task", **When** task exists, **Then** agent confirms destructive action: "⚠️ Delete 'buy milk'? This cannot be undone. Reply 'yes' to confirm."

2. **Given** user confirms deletion, **When** confirmation received, **Then** agent calls `delete_task` and confirms "✅ Deleted 'buy milk'"

3. **Given** user says "delete" without specifying task, **When** intent is ambiguous, **Then** agent requests clarification before proceeding

---

### User Story 5 - Context-Aware Follow-ups (Priority: P3)

User references previous conversation context without repeating details.

**Why this priority**: Enhances UX but not essential for MVP. Depends on conversation memory being functional.

**Independent Test**: Can be tested by creating a task, then saying "move it to tomorrow" and verifying agent understands "it" refers to the just-created task.

**Acceptance Scenarios**:

1. **Given** user just created "buy milk" task, **When** user says "actually, make it tomorrow", **Then** agent resolves "it" to last created task and updates due date

2. **Given** user asks "what's on my list?", **When** user follows with "mark the first one done", **Then** agent resolves "first one" to the first task in the previous list response

---

### Edge Cases

- What happens when user provides ambiguous natural language (e.g., "do the thing")? → Agent MUST request clarification
- How does agent handle dates in different formats (e.g., "tomorrow", "Jan 30", "next week")? → Agent parses all common formats and requests clarification if unparseable
- What happens when user references non-existent task (e.g., "delete xyz task")? → Agent responds "❓ I couldn't find a task called 'xyz'. Here are your current tasks: [list]"
- What happens when database/MCP tool fails? → Agent responds "⚠️ Unable to save changes. Please try again." (no internal errors exposed)
- What happens when user says something completely unrelated (e.g., "what's the weather?")? → Agent politely redirects: "I'm here to help with your todo list. Try 'add task', 'show my tasks', or 'mark task done'."

---

## Requirements

### Functional Requirements

- **FR-001**: Agent MUST detect user intent from natural language input (CREATE, READ, UPDATE, COMPLETE, DELETE)
- **FR-002**: Agent MUST extract task parameters from natural language (title, description, due_date, reminder_time)
- **FR-003**: Agent MUST map detected intents to appropriate MCP tool calls (add_task, list_tasks, update_task, complete_task, delete_task)
- **FR-004**: Agent MUST confirm successful operations in natural language (e.g., "✅ Created task: 'buy milk'")
- **FR-005**: Agent MUST request clarification when intent is ambiguous (e.g., "Which task did you mean?")
- **FR-006**: Agent MUST handle errors gracefully without exposing internal details (e.g., "⚠️ Unable to save changes")
- **FR-007**: Agent MUST NOT write to database directly (all mutations via MCP tools only)
- **FR-008**: Agent MUST reconstruct conversation context from database on every request (stateless between requests)
- **FR-009**: Agent MUST confirm destructive operations before execution (e.g., delete requires user confirmation)
- **FR-010**: Agent MUST parse common date/time formats (relative: "tomorrow", "next week"; absolute: "Jan 30", "2026-01-30")
- **FR-011**: Agent MUST resolve contextual references when possible (e.g., "it", "the first one") using conversation history
- **FR-012**: Agent MUST NOT expose internal prompts, system messages, or reasoning traces to end users
- **FR-013**: Agent MUST preserve all Phase-II functionality (Phase-II APIs continue working unchanged)

### Key Entities

- **Intent**: Detected user goal (CREATE, READ, UPDATE, COMPLETE, DELETE, CLARIFY, ERROR)
  - Attributes: intent_type, confidence_score, extracted_parameters
  - Derived from: Natural language input + conversation context

- **TaskParameters**: Extracted task information from user input
  - Attributes: title (string), description (optional string), due_date (optional datetime), reminder_time (optional datetime)
  - Mapped to: MCP tool input schemas

- **ConversationContext**: Historical context for resolving ambiguous references
  - Attributes: recent_messages, last_created_task, last_listed_tasks
  - Source: Reconstructed from database on every request (stateless)

- **AgentResponse**: Natural language output to user
  - Attributes: message_text, response_type (confirmation, clarification, error)
  - Format: User-friendly natural language (no technical jargon)

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can create tasks in under 10 seconds using natural language (vs 30+ seconds with forms)
- **SC-002**: Agent correctly identifies intent with 90%+ accuracy on common task management phrases
- **SC-003**: Agent requests clarification instead of guessing when confidence < 70%
- **SC-004**: Zero database write operations occur outside of MCP tool calls (verified via database audit logs)
- **SC-005**: Agent confirms 100% of destructive operations (delete) before execution
- **SC-006**: Agent handles 100% of MCP tool errors without exposing internal details to users
- **SC-007**: Agent resolves contextual references ("it", "that task") correctly 80%+ of the time when context exists
- **SC-008**: Conversation context reconstruction completes in under 500ms for 50-message conversations
- **SC-009**: System survives server restart without losing agent functionality (stateless validation)
- **SC-010**: 95% of user messages receive a response within 3 seconds

---

## Intent Detection Rules

### Intent Mapping Table

| User Phrase Examples | Detected Intent | MCP Tool Called | Parameters Extracted |
|---------------------|-----------------|-----------------|---------------------|
| "add task", "remind me to", "create task" | CREATE | add_task | title, description, due_date, reminder_time |
| "show tasks", "what's next", "my list" | READ | list_tasks | filters (completed, due_date) |
| "update task", "change task", "move to" | UPDATE | update_task | task_id, updated_fields |
| "mark done", "complete task", "finished" | COMPLETE | complete_task | task_id |
| "delete task", "remove task", "cancel task" | DELETE | delete_task | task_id (requires confirmation) |

### Clarification Triggers

Agent MUST request clarification when:

1. **Ambiguous Task Reference**: User says "delete task" without specifying which task
2. **Low Confidence Intent**: Intent detection confidence < 70%
3. **Missing Required Parameters**: User says "add task" without providing a title
4. **Multiple Matches**: User says "update report task" and 3 tasks contain "report"
5. **Unparseable Date**: User provides date in unrecognizable format

### Confirmation Requirements

Agent MUST confirm before executing:

1. **Delete Operations**: Always require explicit "yes" confirmation
2. **Batch Operations**: Any operation affecting >1 task requires confirmation
3. **High-Impact Changes**: Operations that cannot be easily undone

---

## Error Handling Specifications

### Error Response Format

All error responses MUST:
- Use ⚠️ emoji prefix
- Provide user-friendly explanation (no stack traces, no internal errors)
- Suggest corrective action when possible
- Never expose database connection strings, API keys, or internal system details

### Error Scenarios

| Error Condition | User-Facing Response | Internal Action |
|----------------|---------------------|----------------|
| MCP tool returns 500 error | "⚠️ Unable to save changes. Please try again." | Log error, do not retry automatically |
| MCP tool returns 404 (task not found) | "❓ I couldn't find that task. Here are your current tasks: [list]" | Log, provide task list for context |
| Database connection timeout | "⚠️ Having trouble connecting. Please try again in a moment." | Log error, do not expose timeout details |
| Invalid date format | "❓ I didn't understand that date. Try formats like 'tomorrow', 'Jan 30', or '2026-01-30'." | Provide examples of valid formats |
| Agent reasoning failure | "❓ I'm not sure what you'd like to do. Try 'add task', 'show my tasks', or 'mark task done'." | Log failure, redirect to known commands |

---

## Natural Language Processing Requirements

### Date Parsing

Agent MUST support:

**Relative Dates**:
- "today", "tomorrow", "yesterday"
- "next week", "next month"
- "monday", "tuesday", etc. (next occurrence)
- "in 3 days", "in 2 weeks"

**Absolute Dates**:
- "Jan 30", "January 30", "1/30", "01/30/2026"
- "2026-01-30" (ISO format)

**Time Parsing**:
- "3pm", "15:00", "3:30pm"
- "morning" (9am), "afternoon" (2pm), "evening" (6pm)

### Title Extraction

Agent MUST extract task title from common patterns:

- "add [title]" → title
- "remind me to [title]" → title
- "create task [title]" → title
- "new task: [title]" → title

### Context Resolution

Agent MUST resolve pronouns/references:

- "it" → last mentioned task
- "that task" → last mentioned task
- "the first one" → first task in last list
- "the milk task" → task with "milk" in title

---

## Assumptions

1. Users will primarily use common task management vocabulary (add, show, mark done, delete)
2. Date references are in user's local timezone (timezone detection out of scope for Phase III)
3. Natural language input is in English (multilingual support out of scope)
4. Users will provide task titles that are 1-50 words (longer titles truncated with warning)
5. Agent does not need to handle voice input (text-based only for Phase III)
6. Conversation history limited to last 50 messages for context reconstruction (performance constraint)

---

## Out of Scope for Phase III

- Voice input/output
- Multilingual support (non-English languages)
- Integration with external calendar systems
- Advanced NLP features (sentiment analysis, entity recognition beyond tasks)
- Proactive reminders (agent initiating conversations)
- Task sharing/collaboration features
- File attachments or rich media in tasks

---

## Dependencies

**Phase II Components** (must remain functional):
- Task CRUD APIs (`/api/v1/tasks/`)
- User authentication (Better Auth)
- Database schema (`tasks`, `users`, `auth` tables)

**Phase III Components** (dependencies for this spec):
- MCP Server Spec (spec-6): Provides tool interfaces this agent will call
- Persistence & Memory Spec (spec-7): Provides conversation context for reconstruction

**External Services**:
- OpenAI API: For natural language understanding (agent uses OpenAI Agents SDK)
- Neon Database: For conversation context storage and task data

---

## Validation & Testing Strategy

### Unit Tests

- Intent detection accuracy (test with 100+ labeled user phrases)
- Parameter extraction from natural language (test date parsing, title extraction)
- Error handling responses (verify no internal details exposed)

### Integration Tests

- Agent → MCP tool → Database flow (end-to-end task creation)
- Context reconstruction from database (verify stateless operation)
- Confirmation flow for destructive operations

### End-to-End Tests

- Full conversation flows (create → list → update → complete → delete)
- Error scenarios (database down, MCP tool failures)
- Context resolution across multiple messages

### Performance Tests

- Context reconstruction under 500ms for 50-message conversations
- Intent detection under 1 second for common phrases
- Response time under 3 seconds for 95% of requests

---

## Acceptance Criteria

**This specification is ready for planning when**:

1. All user stories have testable acceptance scenarios
2. All functional requirements are unambiguous and verifiable
3. All error scenarios have defined user-facing responses
4. Intent mapping table is complete with common user phrases
5. No [NEEDS CLARIFICATION] markers remain
6. Success criteria are measurable and technology-agnostic
7. Dependencies on other Phase III components are explicitly stated
8. Phase-II protection requirements are documented

**Planning phase should validate**:

1. OpenAI Agents SDK capabilities match intent detection requirements
2. MCP tool schemas support all extracted parameters
3. Database schema supports conversation context reconstruction
4. Performance targets are achievable with proposed architecture
