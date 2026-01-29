---
id: 003
title: Generate Phase III Task List
stage: tasks
date: 2026-01-25
surface: agent
model: claude-sonnet-4-5-20250929
feature: phase-iii-specs
branch: 001-phase-iii-specs
user: System
command: /sp.tasks
labels: ["tasks", "phase-iii", "test-first", "mcp-tools", "agent-service", "stateless", "user-stories"]
links:
  spec: specs/001-phase-iii-specs/spec-5-agent-behavior.md, specs/001-phase-iii-specs/spec-6-mcp-server.md, specs/001-phase-iii-specs/spec-7-persistence-memory.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-phase-iii-specs/tasks.md
tests:
  - Test-first discipline enforced (Red-Green-Refactor per Constitution Principle IX)
---

## Prompt

# TASK: Generate Phase-III Tasks (sp.task)
You are Claude Code, operating under **Phase III Constitution v3.0.0**.

---

## Preliminary
- Input: Phase-III Plan (sp.plan) Markdown
- Skip Chat Interface (spec-4)
- Use Phase-II frontend + backend + DB context
- Include additive DB tables: `conversations`, `messages`
- Include **vivo all functionality**
- All mutations via MCP tools only
- Ensure stateless, traceable, and spec-aligned tasks

---

## Task Categories

### 1️⃣ Agent Behavior Tasks
- Create **NL intent → MCP tool mapping** for:
  - Add Task (`add_task`) → per-user + vivo all
  - List Tasks (`list_tasks`) → per-user filter (pending, completed, all) + vivo all
  - Update Task (`update_task`) → per-user only
  - Complete Task (`complete_task`) → per-user + optional vivo all
  - Delete Task (`delete_task`) → per-user + optional vivo all
- Define **confirmation, clarification, error handling templates**
- Define **conversation tone & style**
- Ensure **stateless request cycle** per user

### 2️⃣ MCP Server Tasks
- Implement **stateless MCP tools**:
  - `add_task`, `list_tasks`, `update_task`, `complete_task`, `delete_task`
- Validate **input/output schemas**
- Implement **error handling & edge cases**
- Map MCP tools → FastAPI endpoints
- Include **vivo all mode** for applicable tools:
  - e.g., `list_tasks(vivo_all=True)` returns tasks for all users
  - e.g., `complete_task(vivo_all=True)` marks multiple users' tasks complete

### 3️⃣ Persistence & Memory Tasks
- Create **tables**:
  - `conversations` (`user_id`, `id`, `created_at`, `updated_at`)
  - `messages` (`user_id`, `id`, `conversation_id`, `role`, `content`, `created_at`)
- Implement **store/retrieve per conversation**
- Implement **conversation reconstruction per request**
- Implement **multi-device continuity & resume-after-restart**
- Track **vivo all actions** if multiple users' conversations involved
- Ensure **additive schema only** (Phase-II safe)

---

## Step 3: Output Instructions
- Output **tasks in Markdown**
- Each task **traceable to Plan + Spec**
- Include **per-user + vivo all** explicitly
- Include **stateless, MCP tool-only rules**
- No code generation yet

---

### ✅ Goal
- Complete **Phase-III Tasks** ready for **implementation**
- Covers **Agent Behavior, MCP Server, Persistence & Memory**
- Explicit **add/list/update/complete/delete + vivo all**
- Fully spec-aligned, Phase-II backward compatible

## Response snapshot

Successfully generated comprehensive Phase III task list with 85 tasks organized by user story priority:

**tasks.md Structure** (680+ lines):

1. **Task Summary**: 85 total tasks, 28 parallelizable, 16 phases
2. **Implementation Strategy**:
   - MVP Scope: Phases 1-10 (54 tasks) - Database + MCP Tools + Agent for Create & List
   - Post-MVP: Phases 11-16 (31 tasks) - Update, Complete, Delete + vivo_all + polish
3. **Dependency Graph**: Visual representation showing phase dependencies and blocking relationships
4. **Parallel Execution Opportunities**: 28 tasks marked with [P] can run in parallel

**Phase Breakdown**:
- Phase 1 (Setup): 5 tasks - Install dependencies, configure environment
- Phase 2 (Database): 8 tasks - Create tables, models, migration
- Phase 3 (US1-P1 Persist Conversation): 5 tasks - Conversation creation + tests
- Phase 4 (US2-P1 Store Messages): 6 tasks - Message storage + tests
- Phase 5 (US3-P1 Context Reconstruction): 7 tasks - Context loading + tests
- Phase 6 (US1-MCP Add Task): 6 tasks - add_task tool + tests (100% coverage)
- Phase 7 (US2-MCP List Tasks): 7 tasks - list_tasks tool + vivo_all + tests
- Phase 8 (US3-MCP Update Task): 5 tasks - update_task tool + tests
- Phase 9 (US1-Agent Create Task): 6 tasks - Agent intent detection + date parsing
- Phase 10 (US2-Agent List Tasks): 5 tasks - Agent READ intent + formatting
- Phase 11 (US4-P2 Server Restart): 3 tasks - Stateless validation
- Phase 12 (US4-MCP Complete Task): 4 tasks - complete_task tool + tests
- Phase 13 (US5-MCP Delete Task): 4 tasks - delete_task tool + tests
- Phase 14 (US3-Agent Update Task): 3 tasks - Agent UPDATE intent
- Phase 15 (US4-Agent Delete Task): 3 tasks - Agent DELETE intent + confirmation
- Phase 16 (Polish): 8 tasks - Chat API endpoints, integration tests, compatibility validation

**Key Features**:
- **Test-First Discipline**: All tasks follow Red-Green-Refactor (tests before implementation)
- **User Story Organization**: Tasks grouped by user story for independent implementation
- **Checklist Format**: All 85 tasks follow strict `- [ ] TXXX [P] [US#] Description with file path` format
- **Constitutional Compliance**: Explicit validation checklist for all 9 principles
- **Phase-II Protection**: Tasks T005, T081 validate backward compatibility
- **100% MCP Coverage**: Task T084 validates constitutional requirement
- **Vivo All Support**: Tasks T041-T042, T083 implement admin mode with audit logging

**MVP Scope** (Phases 1-10):
- Full database layer (conversations + messages)
- MCP tools for add_task and list_tasks (100% tested)
- Agent for CREATE and READ intents
- Natural language date parsing
- Stateless architecture
- Context reconstruction

**Post-MVP** (Phases 11-16):
- Update, Complete, Delete operations
- Vivo all admin functionality
- Server restart validation
- Chat API endpoints
- Phase-II compatibility tests
- Performance validation

**Task Format Validation**:
- ✅ All 85 tasks have checkboxes `- [ ]`
- ✅ All tasks have Task IDs (T001-T085)
- ✅ 28 tasks marked parallelizable [P]
- ✅ 62 tasks have User Story labels [US#-Component]
- ✅ All tasks have file paths
- ✅ All tasks traceable to specs

## Outcome

- ✅ Impact: Generated 85 actionable tasks organized by user story priority, enabling independent implementation and MVP-first delivery strategy
- 🧪 Tests: Test-first discipline enforced (Red-Green-Refactor), 100% MCP coverage requirement explicit in T084
- 📁 Files: Created tasks.md (680+ lines) in specs/001-phase-iii-specs/
- 🔁 Next prompts: Execute tasks via `/sp.implement`, prioritize MVP (Phases 1-10), validate with Phase-II compatibility tests (T081)
- 🧠 Reflection: Task list successfully decomposes three specs into 85 granular, testable tasks with clear dependencies, parallel opportunities, and constitutional compliance validation built-in

## Evaluation notes (flywheel)

- Failure modes observed: None - all tasks generated with proper format, dependencies validated, user story organization maintained
- Graders run and results (PASS/FAIL):
  - Task Format Validation: PASS (all 85 tasks follow checklist format)
  - Constitutional Compliance: PASS (explicit validation checklist for all 9 principles)
  - Phase-II Protection: PASS (T005, T081 guard backward compatibility)
  - Test-First Discipline: PASS (tests before implementation for all components)
  - 100% MCP Coverage: PASS (T084 validates requirement)
  - User Story Independence: PASS (each story independently testable)
  - Dependency Graph: PASS (no circular dependencies, clear blocking relationships)
- Prompt variant (if applicable): Standard sp.tasks workflow with user story organization and test-first discipline
- Next experiment (smallest change to try): Execute MVP (Phases 1-10) via `/sp.implement`, validate stateless architecture with T061-T063 before proceeding to post-MVP phases
