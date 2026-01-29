# Phase III Specifications: AI-Powered Conversational Todo Management

**Branch**: `001-phase-iii-specs`
**Created**: 2026-01-25
**Status**: Ready for Planning
**Constitution**: Phase III Constitution v3.0.0

## Overview

Phase III extends the completed Phase-II full-stack Todo application with AI-powered conversational task management capabilities. This feature set enables users to create, read, update, and delete tasks through natural language conversation with an AI agent.

## Specification Structure

Phase III follows the **Spec Decomposition Rule** (Constitution Principle VII), which mandates separate specifications for each architectural concern:

| Spec | File | Responsibility | Status |
|------|------|---------------|--------|
| **Agent Behavior** | `spec-5-agent-behavior.md` | Natural language understanding, intent detection, MCP tool orchestration | ✅ Ready |
| **MCP Server** | `spec-6-mcp-server.md` | Stateless database tools for task CRUD operations | ✅ Ready |
| **Persistence & Memory** | `spec-7-persistence-memory.md` | Conversation storage and stateless context reconstruction | ✅ Ready |

**Note**: Chat Interface Spec (spec-4) already exists in the project per task instructions.

## Constitutional Compliance

All three specifications strictly adhere to the Phase III Constitution v3.0.0:

### Core Principles Applied

1. **Agentic Dev Stack (Principle I)**: All specs ready for `/sp.plan` → `/sp.tasks` → `/sp.implement` workflow
2. **Spec-Driven Authority (Principle II)**: Specs define all behavior, no implementation assumptions
3. **Stateless Architecture (Principle III)**: No in-memory state, context reconstructed from database every request
4. **Tool-Only Mutation Rule (Principle IV)**: Agent → MCP tools → Database (no direct writes)
5. **Clear Responsibility Separation (Principle V)**: Agent = reasoning, MCP = mutations, Database = memory
6. **Phase-II Protection (Principle VI)**: Only additive changes (new tables: conversations, messages), existing APIs unchanged
7. **Spec Decomposition Rule (Principle VII)**: Three separate specs as required
8. **Agent Behavior Standards (Principle VIII)**: Transparency, confirmation, graceful errors mandatory
9. **Test-First Discipline (Principle IX)**: All specs include comprehensive testing strategies

## Architecture Overview

```
User Message
     ↓
Chat API (FastAPI)
     ↓ (reconstruct context from DB)
Database: conversations, messages
     ↓ (provides context)
Agent (OpenAI Agents SDK)
     ↓ (detects intent)
MCP Tools (Official MCP SDK)
     ↓ (CRUD operations)
Database: tasks
     ↓
Agent Response
     ↓
Chat API
     ↓ (store message)
Database: messages
     ↓
User
```

### Key Architectural Guarantees

- **Stateless**: Server can restart without losing functionality
- **Persistent**: All conversations and context stored in Neon DB
- **Secure**: Tool-only mutations prevent unauthorized database access
- **Extensible**: Additive changes preserve Phase-II functionality

## Database Schema Extensions

Phase III adds TWO new tables to existing Neon database:

### conversations
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    UNIQUE(user_id)  -- One conversation per user (MVP)
);
```

### messages
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(10) NOT NULL CHECK (role IN ('user', 'agent')),
    content TEXT NOT NULL CHECK (LENGTH(content) <= 10000),
    created_at TIMESTAMP NOT NULL
);
```

**Existing tables remain unchanged**: `tasks`, `users`, `auth`, `priorities`, `tags`

## MCP Tools Defined

Phase III defines 5 stateless MCP tools for task management:

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `add_task` | Create new task | title, description, due_date, reminder_time, user_id | Created task object |
| `list_tasks` | Query tasks with filters | user_id, completed, due_date, priority_id, limit, offset | Task array + total |
| `update_task` | Update task fields | task_id, user_id, fields to update | Updated task object |
| `complete_task` | Mark task done | task_id, user_id | Updated task object |
| `delete_task` | Remove task | task_id, user_id | Success confirmation |

All tools enforce user authorization (tasks belong to user_id), use transactions, and return standardized errors.

## Agent Capabilities

The AI agent (OpenAI Agents SDK) supports:

### Intent Detection
- CREATE: "add buy milk", "remind me to call dentist"
- READ: "show my tasks", "what's due today"
- UPDATE: "move milk task to tomorrow"
- COMPLETE: "mark milk done"
- DELETE: "delete milk task" (requires confirmation)

### Natural Language Processing
- Date parsing: "tomorrow", "next week", "Jan 30", "2026-01-30"
- Time parsing: "3pm", "15:00", "morning"
- Context resolution: "it", "that task", "the first one"

### User Experience
- ✅ Confirmation after successful operations
- ❓ Clarification requests for ambiguous inputs
- ⚠️ Graceful error messages (no internal details exposed)

## Success Criteria Summary

### Agent Behavior (spec-5)
- Intent detection: 90%+ accuracy
- Task creation: < 10 seconds via natural language
- Context resolution: 80%+ accuracy
- Response time: < 3 seconds for 95% of requests

### MCP Server (spec-6)
- Operation latency: < 200ms for 95%
- Concurrent requests: 1000+ without errors
- Test coverage: 100% for all tools
- Zero direct database writes (verified via audit logs)

### Persistence & Memory (spec-7)
- Context reconstruction: < 500ms for 50-message conversations
- Server restart: Zero message loss
- Zero in-memory state between requests
- 1000+ concurrent reconstructions without degradation

## Next Steps

### 1. Planning Phase (`/sp.plan`)
Run planning for each specification separately:
```bash
/sp.plan --spec spec-5-agent-behavior.md
/sp.plan --spec spec-6-mcp-server.md
/sp.plan --spec spec-7-persistence-memory.md
```

Each plan should:
- Validate technology choices (OpenAI Agents SDK, Official MCP SDK, SQLModel)
- Design database migrations (add conversations, messages tables)
- Define API contracts (chat endpoint, MCP tool signatures)
- Identify ADR candidates (stateless architecture, one-conversation-per-user)

### 2. Task Generation (`/sp.tasks`)
Generate testable tasks for each plan:
- Red phase: Write failing tests
- Green phase: Implement to pass tests
- Refactor phase: Optimize and clean up

### 3. Implementation (`/sp.implement`)
Execute tasks via Claude Code following constitution

### 4. Review
- Validate Phase-II APIs unchanged
- Verify stateless architecture (server restart test)
- Confirm 100% test coverage for MCP tools
- Performance test context reconstruction

## Dependencies

### Phase II (Completed)
- Task CRUD APIs: `/api/v1/tasks/`
- User authentication: Better Auth
- Database: Neon Serverless PostgreSQL
- Frontend: Next.js Todo App

### Phase III (This Feature)
- OpenAI Agents SDK: Agent reasoning
- Official MCP SDK (Python): Tool layer
- OpenAI ChatKit: Frontend chat interface (separate spec)

## Assumptions Across All Specs

1. One conversation per user (MVP constraint, may be relaxed later)
2. English language only (multilingual out of scope)
3. Text-based interaction (voice input out of scope)
4. Last 50 messages for context (performance vs completeness tradeoff)
5. User timezone handling by client (backend stores UTC)
6. No multi-user conversation sharing (single-user todos)

## Out of Scope for Phase III

- Voice input/output
- Multilingual support
- Multiple conversations per user (thread management)
- Task collaboration/sharing
- File attachments or rich media
- Proactive reminders (agent-initiated conversations)
- Integration with external calendar systems

## Validation Checklist

Before proceeding to planning phase, verify:

- [x] All three specs have complete user stories with acceptance scenarios
- [x] All functional requirements are testable and unambiguous
- [x] All success criteria are measurable and technology-agnostic
- [x] All error scenarios have defined handling strategies
- [x] Database schema changes are explicitly documented
- [x] Phase-II protection requirements stated
- [x] Constitutional compliance documented per spec
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Dependencies between specs are explicit
- [x] Testing strategies cover unit, integration, E2E, and performance

## Contact

**Feature Owner**: Phase III Development Team
**Constitution Version**: 3.0.0
**Architecture Review**: Required before implementation
**Security Review**: Required for MCP tool authorization logic

---

**Ready for Planning**: All specifications are complete and validated against Phase III Constitution. Proceed with `/sp.plan` for each spec to generate implementation plans.
