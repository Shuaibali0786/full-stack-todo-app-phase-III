---
id: 002
title: Generate Phase III Implementation Plan
stage: plan
date: 2026-01-25
surface: agent
model: claude-sonnet-4-5-20250929
feature: phase-iii-specs
branch: 001-phase-iii-specs
user: System
command: /sp.plan
labels: ["plan", "phase-iii", "architecture", "mcp-tools", "agent-service", "stateless", "vivo-all"]
links:
  spec: specs/001-phase-iii-specs/spec-5-agent-behavior.md, specs/001-phase-iii-specs/spec-6-mcp-server.md, specs/001-phase-iii-specs/spec-7-persistence-memory.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-phase-iii-specs/plan.md
tests:
  - None (planning phase, tests defined in plan)
---

## Prompt

# TASK: Generate Phase-III Plan (sp.plan)
You are Claude Code, operating under the **Phase III Constitution v3.0.0**.

---

## Step 0: Preliminary Checks
1. Analyze **existing Phase-II code** (frontend + backend + DB).
2. **Skip spec-4 (Chat Interface Spec)** — already exists.
3. Phase-III is additive only:
   - Add **Agent Behavior Spec**
   - Add **MCP Server Spec**
   - Add **Persistence & Memory Spec**
4. Database:
   - Reuse existing Neon DB (`users`, `tasks`, `auth`)
   - Additive tables: `conversations`, `messages`
   - All mutations go via **MCP tools only**
5. Multi-user support:
   - All MCP tools must support **per-user operations**
   - Include **`vivo all` functionality** to query or act across all users if needed

---

## Step 1: Define Plan Objectives
- Convert **Phase-III specs** into actionable tasks for Claude Code.
- Ensure **stateless architecture**, **tool-only mutation**, **traceable implementation**.
- Respect **Phase-II backward compatibility**.
- Cover **Agent Behavior, MCP Server, Persistence & Memory**.
- Include **full task CRUD support + vivo all operations**.

---

## Step 2: Plan Structure
Create **a step-by-step, high-level plan** with the following sections:

### 1️⃣ Agent Behavior Plan
- Map **user natural language → MCP tool invocation**
- Define rules for:
  - Add Task → `add_task` (supports `vivo all` if needed)
  - List Tasks → `list_tasks` (filter by `pending`, `completed`, `all`, or `vivo all`)
  - Update Task → `update_task`
  - Complete Task → `complete_task`
  - Delete Task → `delete_task`
- Include **confirmation, clarification, error handling rules**
- Include **conversation tone & style**
- Ensure **per-user context + vivo all context**

### 2️⃣ MCP Server Plan
- Plan creation of **stateless MCP tools**
- Input/Output schemas for each tool
- Ensure **tool-only mutation rule**
- Include **error handling, validations, edge cases**
- Map tools to backend endpoints (FastAPI)
- Include **vivo all behavior for each tool**:
  - e.g., `list_tasks(vivo_all=True)` returns tasks for all users
  - e.g., `complete_task(vivo_all=True)` marks multiple users' tasks as complete (optional admin mode)

### 3️⃣ Persistence & Memory Plan
- Plan **conversation & message storage**:
  - Conversation table: `user_id`, `id`, `created_at`, `updated_at`
  - Message table: `user_id`, `id`, `conversation_id`, `role`, `content`, `created_at`
- Define **reconstruction rules** per request (stateless)
- Plan for **multi-device continuity**
- Plan **resume-after-restart** behavior
- Ensure **DB additive schema changes only**
- Include **vivo all tracking** if multiple users' conversations need aggregation

---

## Step 3: Output Instructions
- Generate a **Markdown plan** with:
  - Clear step numbers
  - Task breakdown per spec
  - Additive highlights
  - References to existing Phase-II components
- **Do NOT generate code yet**
- Each plan item must be actionable and traceable to a spec
- Include **full CRUD + vivo all functionality** clearly marked

---

### ✅ Goal
- A complete **Phase-III plan** in Markdown
- Ready to be converted into **sp.task → sp.implement**
- Skips Chat Interface (spec-4)
- Covers **Agent Behavior, MCP Server, Persistence & Memory**
- Includes **add/list/update/complete/delete tasks + vivo all support**
- Fully aligned with Hackathon II/III workflow

## Response snapshot

Successfully generated comprehensive Phase III implementation plan covering all three architectural components:

**plan.md Structure** (845 lines):

1. **Executive Summary**: Stateless architecture, tool-only mutations, additive schema
2. **Constitution Check**: All 9 principles validated (✅ PASS)
3. **Technical Context**: Python 3.10+, FastAPI, OpenAI Agents SDK, MCP SDK, SQLModel
4. **Project Structure**: 17 new files (2 models, 3 services, 1 API, 1 util, 2 migrations, 6 tests, 2 docs)
5. **Phase 0: Research** (5 research tasks):
   - R1: OpenAI Agents SDK integration pattern
   - R2: Official MCP SDK Python implementation
   - R3: Natural language date parsing strategy
   - R4: Vivo All security architecture
   - R5: Database migration zero-downtime strategy
6. **Phase 1: Design & Contracts**:
   - Database schema (conversations, messages tables with SQL + SQLModel)
   - API contracts (chat_api.yaml, mcp_tools.json)
   - Quickstart guide
   - Agent context update script
7. **Phase 2: Implementation Roadmap**:
   - 5-step implementation sequence (Database → MCP → Agent → Chat API → Validation)
   - File creation checklist (17 new files)
8. **Vivo All Implementation**: Tool-level parameter with is_admin role check, audit logging
9. **Testing Strategy**: 6 test suites (50+ tests), 100% MCP coverage requirement
10. **Success Criteria Validation**: Methods for validating all specs' success criteria
11. **ADR Candidates**: 4 architectural decisions identified
12. **Risk Analysis**: 4 top risks with mitigations

**Key Architectural Decisions**:
- Stateless backend: Context from DB every request (no in-memory state)
- Tool-only mutations: Agent → MCP tools → Database (exclusive path)
- Additive schema: conversations + messages tables, Phase-II tables unchanged
- Vivo All: Tool parameter with role-based authorization + audit logging
- One conversation per user (MVP constraint, UNIQUE constraint)

**Constitutional Compliance**:
- All 9 principles validated and passing
- No violations or complexity justifications needed
- Phase-II protection: Zero breaking changes
- Test-first discipline: 100% MCP coverage + comprehensive test strategy

**Technology Stack**:
- Existing: FastAPI, SQLModel, Neon PostgreSQL, Better Auth
- New: openai-agents-sdk, mcp-python-sdk, dateparser

**Implementation Sequence**:
1. Database Layer (Conversation + Message models, migration)
2. MCP Server (5 tools: add, list, update, complete, delete)
3. Agent Service (OpenAI Agent + intent detection + date parsing)
4. Chat API (POST /chat/message, GET /chat/history)
5. Validation (tests, stateless check, Phase-II compatibility)

## Outcome

- ✅ Impact: Generated comprehensive 845-line implementation plan defining complete Phase III architecture with clear dependencies, sequencing, and validation criteria
- 🧪 Tests: Test strategy defined (6 test suites, 50+ tests, 100% MCP coverage requirement)
- 📁 Files: Created plan.md in specs/001-phase-iii-specs/
- 🔁 Next prompts: Phase 0 research tasks to resolve unknowns, then `/sp.tasks` to generate actionable task list
- 🧠 Reflection: Plan successfully bridges three specs (Agent, MCP, Persistence) into unified implementation roadmap with constitutional compliance, vivo_all security, and stateless architecture validated

## Evaluation notes (flywheel)

- Failure modes observed: None - plan generated with all required sections, constitutional validation passed
- Graders run and results (PASS/FAIL):
  - Constitutional Compliance Check: PASS (all 9 principles validated)
  - Phase-II Protection: PASS (additive-only changes documented)
  - Vivo All Security: PASS (role-based authorization with audit logging)
  - Test Coverage Requirements: PASS (100% MCP, 80%+ others)
  - Implementation Sequencing: PASS (dependencies respected)
- Prompt variant (if applicable): Standard sp.plan workflow with vivo_all extension requirement
- Next experiment (smallest change to try): Execute Phase 0 research tasks to resolve OpenAI Agents SDK + MCP SDK integration patterns before task generation
