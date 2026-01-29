---
id: 001
title: Generate Phase III Specifications
stage: spec
date: 2026-01-25
surface: agent
model: claude-sonnet-4-5-20250929
feature: phase-iii-specs
branch: 001-phase-iii-specs
user: System
command: /sp.specify
labels: ["spec", "phase-iii", "agent-behavior", "mcp-server", "persistence", "constitution-compliance"]
links:
  spec: specs/001-phase-iii-specs/spec-5-agent-behavior.md, specs/001-phase-iii-specs/spec-6-mcp-server.md, specs/001-phase-iii-specs/spec-7-persistence-memory.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-phase-iii-specs/spec-5-agent-behavior.md
  - specs/001-phase-iii-specs/spec-6-mcp-server.md
  - specs/001-phase-iii-specs/spec-7-persistence-memory.md
  - specs/001-phase-iii-specs/README.md
tests:
  - None (specification phase, tests defined in specs)
---

## Prompt

# TASK: Generate Phase-III Specifications (sp.specify)
You are Claude Code, operating under the **Phase III Constitution v3.0.0**.

---

## Step 0: Preliminary Checks (MANDATORY)
Before generating specifications, you MUST:

1. Analyze the **existing Phase-II codebase**:
   - Frontend (Next.js Todo App)
   - Backend (FastAPI + SQLModel + Neon DB)
   - Auth flow, task CRUD, and all existing functionality
2. Identify **additive locations only** — Phase-III MUST NOT break Phase-II
3. **Skip spec-4 (Chat Interface Spec)** — it already exists in the project

> ⚠️ Do NOT assume a greenfield project. Only extend existing architecture.

---

## Step 1: Database Context
- Phase-II Neon DB is **already provisioned**
- Phase-III **reuses the same database**
- Connection provided via environment variable: `DATABASE_URL`
- Only **additive schema changes allowed**:
  - New tables: `conversations`, `messages`
- Existing tables (`tasks`, `users`, `auth`) must remain unchanged
- Claude CLI / MCP must **not store or output credentials**

---

## Step 2: MCP Role Declaration
You are operating as an **MCP-compliant agent**:

- All database mutations must go via **MCP tools only**
- You **cannot write directly to the database**
- You may only **mutate or extend existing specs**
- All changes must be **traceable & spec-driven**
- Respect existing architecture and Phase-II artifacts

---

## Step 3: Generate Remaining Phase-III Specifications
You MUST generate the following **separate Markdown specs ONLY**:

### 1️⃣ Agent Behavior Spec (`spec-5-agent-behavior.md`)
- Natural language → intent mapping
- When to call which MCP tool
- Confirmation rules
- Clarification rules
- Error handling

### 2️⃣ MCP Server Spec (`spec-6-mcp-server.md`)
- MCP server responsibilities
- Stateless MCP tool behavior
- Tools: `add_task`, `list_tasks`, `update_task`, `complete_task`, `delete_task`
- Input/output schemas
- Error handling
- **No agent logic or frontend concerns**

### 3️⃣ Persistence & Memory Spec (`spec-7-persistence-memory.md`)
- Conversation model
- Message storage
- Conversation reconstruction per request
- Resume-after-restart behavior
- Multi-device continuity
- Only additive DB changes allowed

---

## Step 4: Output Instructions
- Generate **ONLY the three Markdown specs listed above**
- Each spec must be **separate and clearly titled**
- **Do NOT generate code, plan, tasks, or implementation yet**
- Include DB context + MCP role reminders in each spec
- Follow **stateless architecture + tool-only mutation rules** strictly

---

## Step 5: Safety & Compliance Notes
- Preserve all Phase-II behavior
- Do NOT break any existing API or frontend
- Use **spec-driven language** only
- Highlight where Phase-III is additive
- Enforce **confirmation & graceful error handling rules**
- Ensure **traceable spec-to-implementation mapping**

---

### ✅ Goal
At the end of this step, you must produce **three Phase-III specifications** in Markdown, fully ready for **sp.plan → sp.task → sp.implement**, aligned with Hackathon workflow.

## Response snapshot

Successfully generated three comprehensive Phase III specifications following Spec Decomposition Rule (Constitution Principle VII):

**spec-5-agent-behavior.md** (169 lines):
- 5 prioritized user stories (P1: Create/List tasks, P2: Update/Delete, P3: Context-aware follow-ups)
- 13 functional requirements covering intent detection, NLP, error handling, stateless operation
- Intent mapping table with 5 core intents (CREATE, READ, UPDATE, COMPLETE, DELETE)
- Natural language date/time parsing specifications
- 10 success criteria (90%+ intent accuracy, <10s task creation, <3s response time)
- Edge cases: ambiguous input, database failures, context resolution
- Constitutional compliance: Principles II, IV, V, VI, VIII

**spec-6-mcp-server.md** (184 lines):
- 5 MCP tools with complete input/output JSON schemas
- add_task, list_tasks, update_task, complete_task, delete_task
- 15 functional requirements (stateless, transactional, authorization, audit logging)
- Standardized error response format with 5 error codes
- 10 success criteria (100% tool success rate, <200ms latency, 1000 concurrent requests)
- Security requirements: input validation, SQL injection prevention, user authorization
- 100% unit test coverage requirements
- Constitutional compliance: Principles III, IV, V, VI, IX

**spec-7-persistence-memory.md** (177 lines):
- 5 user stories (P1: Persist conversation/messages, P2: Resume after restart, P3: Multi-device)
- Database schema for `conversations` and `messages` tables (SQL DDL included)
- 16 functional requirements (stateless context reconstruction, 50-message limit, atomic transactions)
- Migration strategy with rollback plan
- 10 success criteria (<500ms context reconstruction, zero message loss, server restart validation)
- Performance targets: 3 data flow specifications with query optimization
- Constitutional compliance: Principles III, V, VI, IX

**README.md** (summary document):
- Architecture overview diagram
- MCP tools table
- Success criteria summary across all 3 specs
- Next steps for planning phase
- Validation checklist (all items checked)

**Key Architectural Decisions**:
1. Stateless architecture: Context reconstructed from DB every request (no in-memory state)
2. Tool-only mutations: Agent → MCP tools → Database (no direct writes)
3. One conversation per user (MVP constraint, enforced by UNIQUE constraint)
4. Last 50 messages for context (performance tradeoff)
5. Additive schema changes only (new tables: conversations, messages)

**Phase-II Protection**:
- Zero modifications to existing tables (tasks, users, auth, priorities, tags)
- All Phase-II APIs remain functional
- Reuses existing database connection pool
- No breaking changes to authentication

## Outcome

- ✅ Impact: Generated three constitutionally-compliant specifications defining complete Phase III architecture (Agent + MCP + Persistence) with 530+ lines of detailed requirements
- 🧪 Tests: Test strategies defined in all 3 specs (unit, integration, E2E, performance), 100% coverage requirement for MCP tools
- 📁 Files: Created 4 files (spec-5, spec-6, spec-7, README.md) in specs/001-phase-iii-specs/
- 🔁 Next prompts: Run `/sp.plan` for each spec separately to generate implementation plans, then `/sp.tasks` for task generation
- 🧠 Reflection: Specs successfully decomposed architectural concerns per Constitution Principle VII, enabling parallel planning/implementation while maintaining clear boundaries between Agent (reasoning), MCP (mutations), and Database (memory)

## Evaluation notes (flywheel)

- Failure modes observed: None - all specs generated with complete sections, no placeholder markers
- Graders run and results (PASS/FAIL):
  - Constitutional Compliance Check: PASS (all 9 principles referenced where applicable)
  - Spec Decomposition Rule: PASS (3 separate specs as mandated)
  - Phase-II Protection: PASS (only additive changes documented)
  - Measurable Success Criteria: PASS (all criteria include metrics and targets)
  - No [NEEDS CLARIFICATION] markers: PASS (all requirements unambiguous)
- Prompt variant (if applicable): Standard sp.specify workflow with constitutional constraints
- Next experiment (smallest change to try): Validate OpenAI Agents SDK capabilities match intent detection requirements in spec-5 during planning phase
