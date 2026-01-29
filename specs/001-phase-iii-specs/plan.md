# Implementation Plan: TaskFlow AI - Intelligent Task Assistant

**Branch**: `001-phase-iii-specs` | **Date**: 2026-01-27 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-phase-iii-specs/spec.md`

## Summary

TaskFlow AI adds conversational natural language interface to the existing Phase II full-stack todo application. Users can create, view, update, and delete tasks through an AI chat assistant powered by OpenRouter API. The system uses keyword-triggered task creation ("add", "create", "make", "new task"), maintains strict user isolation, and provides real-time dashboard synchronization.

**Core Architectural Decisions**:
- OpenRouter API for multi-model LLM support (Claude, GPT, etc.)
- Stateless backend with database-persisted conversation history
- MCP tools for all task database mutations (Tool-Only Mutation Rule)
- WebSocket/SSE for real-time dashboard updates
- Binary task status model (pending/completed)
- Immutable task titles after creation

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/Next.js 14+ (frontend)
**Primary Dependencies**:
- Backend: FastAPI 0.109+, SQLModel 0.0.14+, OpenAI Agents SDK (latest), Official MCP SDK (Python), OpenRouter API client
- Frontend: Next.js 14+, React 18+, WebSocket client for real-time sync
**Storage**: SQLite (existing Phase II: `todo_app.db`) - extended schema for conversations and messages
**Testing**: pytest (backend unit/integration), Jest/React Testing Library (frontend)
**Target Platform**: Web application (browser-based chat + dashboard)
**Project Type**: Web (backend + frontend)
**Performance Goals**:
- <3s OpenRouter API response (p90)
- <1s real-time dashboard sync latency
- <5s end-to-end task creation (user input → dashboard display)
**Constraints**:
- Must preserve all Phase II functionality (backward compatibility)
- Zero cross-user data leakage (strict user isolation)
- Stateless backend (no in-memory session state)
- 95%+ AI intent detection accuracy for task operations
**Scale/Scope**:
- Multi-user application with authentication
- Estimated 100+ tasks per user
- Conversational context window: last 10 messages per user

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Agentic Dev Stack (Strict) ✅
- **Compliance**: All code generation via Claude Code from approved tasks
- **Status**: PASS - This plan follows Spec → Plan → Tasks → Implementation workflow

### Principle II: Spec-Driven Authority ✅
- **Compliance**: Feature behavior defined in `spec.md` (see lines 1-171)
- **Status**: PASS - All requirements traceable to spec

### Principle III: Stateless Architecture ✅
- **Compliance**: Conversation context reconstructed from database on every request
- **Implementation**:
  - `ConversationService` loads conversation history from DB
  - No global variables or session stores for agent state
  - Database schema includes `conversations` and `messages` tables
- **Status**: PASS

### Principle IV: Tool-Only Mutation Rule ✅
- **Compliance**: AI agents CANNOT write to database directly
- **Implementation**: Agent → MCP Tool → Database mutation path
- **MCP Tools Required**:
  - `create_task(user_id, title, status)` → Task creation
  - `list_tasks(user_id, status_filter)` → Task retrieval
  - `update_task_status(task_id, user_id, status)` → Status toggle
  - `delete_task(task_id, user_id)` → Task deletion
  - `find_tasks_by_name(user_id, search_term)` → Fuzzy search for disambiguation
- **Status**: PASS

### Principle V: Clear Responsibility Separation ✅
- **Compliance**:
  - **Chat API** (`/api/v1/ai_chat.py`): HTTP handling, auth validation, response delivery
  - **Agent** (`AgentService`): Natural language understanding, intent detection, MCP tool orchestration
  - **MCP Tools** (`mcp_server.py`): Database mutations (stateless functions)
  - **Database** (SQLite via SQLModel): Persistent storage for tasks, conversations, messages
- **Status**: PASS

### Principle VI: Phase-II Protection ✅
- **Compliance**: All Phase II REST APIs remain unchanged
- **Protected Endpoints**:
  - `/api/v1/tasks/*` (existing CRUD endpoints)
  - `/api/v1/auth/*` (existing auth flows)
  - `/api/v1/users/*` (existing user management)
- **Additive Changes Only**:
  - NEW: `/api/v1/ai/chat` (AI chat endpoint)
  - NEW: `conversations` table
  - NEW: `messages` table
  - EXTENDED: Task model (no breaking changes, all fields optional additions)
- **Status**: PASS

### Principle VII: Spec Decomposition Rule ⚠️
- **Current State**: Single spec file (`spec.md`) for entire TaskFlow AI feature
- **Constitutional Requirement**: Separate specs for:
  1. Chat Interface Spec
  2. Agent Behavior Spec
  3. MCP Server Spec
  4. Persistence & Memory Spec
- **Justification for Deviation**:
  - TaskFlow AI is a cohesive feature with tightly coupled components
  - Splitting into 4 specs would duplicate 70%+ of context across files
  - User stories are already independently testable (P1-P4 priorities)
  - Implementation can proceed incrementally despite unified spec
- **Mitigation**: Plan phases (below) align with constitutional decomposition:
  - Phase 0: Research (covers all technical unknowns)
  - Phase 1: Data Model & Contracts (MCP tools + persistence)
  - Phase 2: Agent Behavior (intent detection logic)
  - Phase 3: Chat Interface (frontend integration)
- **Status**: JUSTIFIED DEVIATION (document in ADR)

### Principle VIII: Agent Behavior Standards ✅
- **Required Behaviors** (from spec):
  - Intent detection with 95% accuracy (FR-003, SC-002)
  - Confirmation after actions (e.g., "✅ Task created: 'Buy groceries'")
  - Graceful error handling (OpenRouter API failures, ambiguous input)
  - Clarification requests for ambiguous deletions (FR-007)
- **Prohibited Behaviors**:
  - No hallucinated task data
  - No destructive operations without confirmation (delete requires ID or disambiguation)
- **Status**: PASS

### Principle IX: Test-First Discipline ✅
- **Test Strategy**:
  - **Unit Tests**: MCP tools (isolated from database via mocking)
  - **Integration Tests**: Agent + MCP tool flows (in-memory SQLite)
  - **E2E Tests**: Chat API → Agent → MCP → Database (full stack)
- **Coverage Requirements**:
  - MCP tools: 100% (all CRUD operations)
  - Agent intent detection: Core paths (create, list, update status, delete)
  - API routes: Auth + happy path + error cases
- **Status**: PASS

### Summary
- **Violations**: 1 (Principle VII - justified with mitigation)
- **Overall Status**: ✅ PASS WITH JUSTIFIED DEVIATION

## Project Structure

### Documentation (this feature)

```text
specs/001-phase-iii-specs/
├── plan.md              # This file (/sp.plan command output)
├── spec.md              # Feature specification (/sp.clarify output)
├── research.md          # Phase 0 output (technology research)
├── data-model.md        # Phase 1 output (database schema)
├── quickstart.md        # Phase 1 output (setup guide)
├── contracts/           # Phase 1 output (API contracts)
│   ├── mcp-tools.json   # MCP tool definitions (JSON Schema)
│   ├── ai-chat-api.yaml # OpenAPI spec for /api/v1/ai/chat
│   └── websocket.yaml   # WebSocket event schema for real-time sync
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── task.py                # Phase II (existing)
│   │   ├── user.py                # Phase II (existing)
│   │   ├── conversation.py        # Phase III (NEW - conversation history)
│   │   └── message.py             # Phase III (NEW - chat messages)
│   ├── services/
│   │   ├── task_service.py        # Phase II (existing)
│   │   ├── agent_service.py       # Phase III (NEW - AI agent logic)
│   │   ├── conversation_service.py # Phase III (NEW - conversation persistence)
│   │   └── mcp_server.py          # Phase III (NEW - MCP tools)
│   ├── api/
│   │   └── v1/
│   │       ├── tasks.py           # Phase II (existing, untouched)
│   │       └── ai_chat.py         # Phase III (NEW - chat endpoint)
│   ├── core/
│   │   ├── config.py              # Extended for OpenRouter API key
│   │   └── database.py            # Phase II (existing)
│   └── main.py                    # Extended to register ai_chat router
└── tests/
    ├── unit/
    │   ├── test_mcp_tools.py      # Phase III (NEW)
    │   └── test_agent_service.py  # Phase III (NEW)
    ├── integration/
    │   └── test_ai_chat_flow.py   # Phase III (NEW)
    └── e2e/
        └── test_ai_chat_api.py    # Phase III (NEW)

frontend/
├── src/
│   ├── app/
│   │   ├── components/
│   │   │   ├── Chat/
│   │   │   │   ├── ChatKit.tsx           # Phase III (NEW - chat interface)
│   │   │   │   ├── MessageList.tsx       # Phase III (NEW)
│   │   │   │   └── MessageInput.tsx      # Phase III (NEW)
│   │   │   └── TaskTable/
│   │   │       └── TaskTable.tsx         # Phase II (existing, add WebSocket listener)
│   │   ├── dashboard/
│   │   │   └── page.tsx                  # Phase II (existing, integrate ChatKit)
│   │   └── tasks/
│   │       └── page.tsx                  # Phase II (existing, untouched)
│   └── services/
│       ├── taskService.ts                # Phase II (existing)
│       ├── aiChatService.ts              # Phase III (NEW - chat API client)
│       └── websocketService.ts           # Phase III (NEW - real-time sync)
└── tests/
    └── components/
        └── Chat/
            └── ChatKit.test.tsx          # Phase III (NEW)
```

**Structure Decision**: Web application (Option 2) with backend and frontend separation. This structure is already established in Phase II and MUST NOT be changed to maintain backward compatibility (Principle VI). Phase III adds new modules alongside existing code without modifying Phase II file structure.

## Complexity Tracking

> **Filled because Constitution Check has 1 violation (Principle VII)**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| **Principle VII**: Single spec instead of 4 separate specs | TaskFlow AI components are tightly coupled: chat UI depends on agent behavior, agent depends on MCP tools, MCP tools depend on persistence schema. Splitting would create 70%+ duplication of context (user stories, functional requirements, edge cases) across files. | Splitting into 4 specs would: (1) Require each spec to duplicate the 5 user stories to maintain traceability, (2) Create circular dependencies (Agent spec references MCP spec, MCP spec references Persistence spec), (3) Complicate review process (reviewer must read 4 files to understand single feature), (4) Violate DRY principle. Current unified spec is 171 lines - manageable size with clear sections. |

## Phase 0: Research & Technical Decisions

### Unknowns to Resolve

1. **OpenRouter API Integration**
   - Research: Best practices for OpenRouter multi-model usage
   - Decisions needed: Model selection strategy, fallback models, rate limiting
   - Output: Recommended models for intent detection (cost/performance tradeoff)

2. **MCP SDK Implementation**
   - Research: Official MCP Python SDK usage patterns
   - Decisions needed: Tool registration, error handling, type safety
   - Output: MCP tool implementation template

3. **Real-Time Dashboard Sync**
   - Research: WebSocket vs Server-Sent Events (SSE) for task updates
   - Decisions needed: Connection management, reconnection strategy, message format
   - Output: Real-time sync architecture diagram

4. **Conversation Context Management**
   - Research: Context window optimization for stateless backend
   - Decisions needed: How many messages to load, summarization strategy
   - Output: Context reconstruction algorithm

5. **Intent Detection Approach**
   - Research: Keyword matching vs LLM-based intent classification
   - Decisions needed: Hybrid approach, accuracy vs latency tradeoff
   - Output: Intent detection flow diagram

### Research Tasks

```text
For each unknown in Technical Context:
  Task: "Research OpenRouter API best practices for multi-model LLM usage in task management chatbots"
  Task: "Research Official MCP Python SDK patterns for stateless tool implementations"
  Task: "Evaluate WebSocket vs SSE for real-time dashboard sync (latency, browser support, reconnection)"
  Task: "Research conversation context optimization techniques for stateless backends"
  Task: "Compare keyword matching vs LLM intent detection for task operations (accuracy, cost, latency)"
```

**Output**: `research.md` with all decisions documented (format: Decision / Rationale / Alternatives Considered)

## Phase 1: Design & Contracts

**Prerequisites**: `research.md` complete

### Data Model

#### New Tables (Phase III)

**conversations**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique conversation ID |
| user_id | UUID | FOREIGN KEY (users.id), NOT NULL | Owner of conversation |
| created_at | DateTime | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Conversation start time |
| updated_at | DateTime | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last message time |

**messages**
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique message ID |
| conversation_id | UUID | FOREIGN KEY (conversations.id), NOT NULL | Parent conversation |
| role | Enum('user', 'assistant') | NOT NULL | Message sender |
| content | Text | NOT NULL | Message text content |
| created_at | DateTime | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Message timestamp |

#### Existing Tables (Phase II - NO CHANGES)

**tasks** - No schema modifications required
- Existing fields: `id`, `user_id`, `title`, `description`, `is_completed`, `due_date`, `reminder_time`, `priority_id`, `created_at`, `updated_at`
- Status mapping: `is_completed = False` → "pending", `is_completed = True` → "completed"

**users** - No schema modifications

### API Contracts

#### MCP Tools (`contracts/mcp-tools.json`)

```json
{
  "tools": [
    {
      "name": "create_task",
      "description": "Creates a new task for the authenticated user",
      "inputSchema": {
        "type": "object",
        "properties": {
          "user_id": {"type": "string", "format": "uuid"},
          "title": {"type": "string", "maxLength": 500},
          "status": {"type": "string", "enum": ["pending", "completed"], "default": "pending"}
        },
        "required": ["user_id", "title"]
      },
      "outputSchema": {
        "type": "object",
        "properties": {
          "id": {"type": "string", "format": "uuid"},
          "title": {"type": "string"},
          "status": {"type": "string"},
          "created_at": {"type": "string", "format": "date-time"}
        }
      }
    },
    {
      "name": "list_tasks",
      "description": "Lists all tasks for the authenticated user, optionally filtered by status",
      "inputSchema": {
        "type": "object",
        "properties": {
          "user_id": {"type": "string", "format": "uuid"},
          "status_filter": {"type": "string", "enum": ["all", "pending", "completed"], "default": "all"}
        },
        "required": ["user_id"]
      },
      "outputSchema": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "id": {"type": "string"},
            "title": {"type": "string"},
            "status": {"type": "string"},
            "created_at": {"type": "string", "format": "date-time"}
          }
        }
      }
    },
    {
      "name": "update_task_status",
      "description": "Toggles task status between pending and completed",
      "inputSchema": {
        "type": "object",
        "properties": {
          "task_id": {"type": "string", "format": "uuid"},
          "user_id": {"type": "string", "format": "uuid"},
          "status": {"type": "string", "enum": ["pending", "completed"]}
        },
        "required": ["task_id", "user_id", "status"]
      },
      "outputSchema": {
        "type": "object",
        "properties": {
          "id": {"type": "string"},
          "status": {"type": "string"},
          "updated_at": {"type": "string", "format": "date-time"}
        }
      }
    },
    {
      "name": "delete_task",
      "description": "Deletes a task by ID (requires user_id for authorization)",
      "inputSchema": {
        "type": "object",
        "properties": {
          "task_id": {"type": "string", "format": "uuid"},
          "user_id": {"type": "string", "format": "uuid"}
        },
        "required": ["task_id", "user_id"]
      },
      "outputSchema": {
        "type": "object",
        "properties": {
          "success": {"type": "boolean"},
          "message": {"type": "string"}
        }
      }
    },
    {
      "name": "find_tasks_by_name",
      "description": "Finds tasks matching a search term (fuzzy match for disambiguation)",
      "inputSchema": {
        "type": "object",
        "properties": {
          "user_id": {"type": "string", "format": "uuid"},
          "search_term": {"type": "string"}
        },
        "required": ["user_id", "search_term"]
      },
      "outputSchema": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "id": {"type": "string"},
            "title": {"type": "string"},
            "status": {"type": "string"}
          }
        }
      }
    }
  ]
}
```

#### AI Chat API (`contracts/ai-chat-api.yaml`)

```yaml
openapi: 3.0.0
info:
  title: TaskFlow AI Chat API
  version: 1.0.0
paths:
  /api/v1/ai/chat:
    post:
      summary: Send message to AI assistant
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  maxLength: 2000
                  example: "add task buy groceries"
              required:
                - message
      responses:
        '200':
          description: AI assistant response
          content:
            application/json:
              schema:
                type: object
                properties:
                  response:
                    type: string
                    example: "✅ Task created: 'buy groceries' (ID: abc-123, Status: pending)"
                  actions:
                    type: array
                    items:
                      type: object
                      properties:
                        type:
                          type: string
                          enum: [TASK_CREATED, TASK_UPDATED, TASK_DELETED]
                        task:
                          type: object
                          properties:
                            id:
                              type: string
                              format: uuid
                            title:
                              type: string
                            status:
                              type: string
                              enum: [pending, completed]
                            created_at:
                              type: string
                              format: date-time
        '401':
          description: Unauthorized (missing or invalid token)
        '429':
          description: Rate limit exceeded
        '500':
          description: OpenRouter API failure or internal error
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

#### WebSocket Events (`contracts/websocket.yaml`)

```yaml
# Real-time task synchronization events
events:
  TASK_CREATED:
    description: New task created via AI chat
    payload:
      type: object
      properties:
        task:
          type: object
          properties:
            id:
              type: string
              format: uuid
            title:
              type: string
            status:
              type: string
              enum: [pending, completed]
            created_at:
              type: string
              format: date-time

  TASK_UPDATED:
    description: Task status toggled via AI chat
    payload:
      type: object
      properties:
        task:
          type: object
          properties:
            id:
              type: string
            status:
              type: string
              enum: [pending, completed]
            updated_at:
              type: string
              format: date-time

  TASK_DELETED:
    description: Task deleted via AI chat
    payload:
      type: object
      properties:
        task_id:
          type: string
          format: uuid
```

### Agent Context Update

Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude` after Phase 1 to add:
- OpenRouter API integration patterns
- MCP tool definitions
- Stateless conversation context reconstruction logic

**Output**: `data-model.md`, `/contracts/*`, `quickstart.md`, updated `.claude/context.md` (or equivalent)

## Phase 2: Implementation Phases (Executed via /sp.tasks)

**Note**: This section outlines the implementation breakdown. Actual tasks generated by `/sp.tasks` command.

### Phase 2.1: Database Schema & MCP Tools
- Create `conversations` and `messages` models
- Implement MCP tools (create_task, list_tasks, update_task_status, delete_task, find_tasks_by_name)
- Write unit tests for MCP tools (100% coverage)

### Phase 2.2: Agent Service & Intent Detection
- Implement `AgentService` with OpenRouter API integration
- Build intent detection logic (keyword matching + LLM classification)
- Implement conversation context reconstruction from database
- Write integration tests for agent + MCP flows

### Phase 2.3: Chat API Endpoint
- Create `/api/v1/ai/chat` FastAPI route
- Implement auth validation and rate limiting
- Add error handling for OpenRouter API failures
- Write E2E tests for chat API

### Phase 2.4: Frontend Chat Interface
- Build `ChatKit.tsx` component
- Implement `aiChatService.ts` for API calls
- Add WebSocket/SSE listener for real-time dashboard updates
- Integrate chat interface into dashboard page

### Phase 2.5: Real-Time Sync & Testing
- Implement WebSocket/SSE for task updates
- Add reconnection logic for dashboard
- Write E2E tests for full chat → dashboard flow
- Validate Phase II backward compatibility

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| OpenRouter API rate limiting | High (blocks all chat functionality) | Medium | Implement retry with exponential backoff, fallback to error message, cache intent detection results |
| Intent detection accuracy <95% | Medium (poor UX, user frustration) | Medium | Hybrid approach (keyword + LLM), extensive test dataset, clarification prompts for ambiguous input |
| Real-time sync connection drops | Medium (dashboard out of sync) | High | Auto-reconnect logic, full task list resync on reconnection, visual indicator for connection status |
| Phase II regression | High (breaks existing functionality) | Low | Comprehensive E2E tests, no modifications to Phase II routes/models, separate feature flag for Phase III |
| Context window exceeds token limits | Low (conversation fails after many messages) | Medium | Limit to last 10 messages, implement summarization for older context |

## Success Metrics

**Phase 0 (Research)**:
- ✅ All 5 technical unknowns resolved with documented decisions
- ✅ ADR created for Principle VII deviation

**Phase 1 (Design)**:
- ✅ Data model supports stateless conversation reconstruction
- ✅ 5 MCP tools defined with complete JSON schemas
- ✅ API contracts pass OpenAPI validation
- ✅ Quickstart guide enables developer setup in <10 minutes

**Phase 2 (Implementation)**:
- ✅ All unit tests pass (MCP tools: 100% coverage)
- ✅ All integration tests pass (agent flows: core paths)
- ✅ All E2E tests pass (chat API → dashboard sync)
- ✅ Phase II regression suite passes (0 failures)
- ✅ Intent detection accuracy ≥95% on test dataset (100 examples)
- ✅ Real-time sync latency <1s (measured via E2E test)
- ✅ OpenRouter API response time <3s (p90)

## Next Steps

1. **Execute Phase 0**: Run research tasks to resolve technical unknowns
2. **Create ADR**: Document Principle VII deviation justification
3. **Execute Phase 1**: Generate data model, contracts, and quickstart
4. **Review & Approve**: Validate plan before proceeding to `/sp.tasks`
5. **Task Generation**: Run `/sp.tasks` to create implementation task list

---

**Plan Status**: ✅ READY FOR REVIEW
**Constitutional Compliance**: ✅ PASS (1 justified deviation documented)
**Estimated Complexity**: MEDIUM (extends existing system, no breaking changes)
