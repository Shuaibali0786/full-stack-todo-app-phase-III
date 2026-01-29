# Tasks: TaskFlow AI - Intelligent Task Assistant

**Feature Branch**: `001-phase-iii-specs` | **Created**: 2026-01-27
**Input**: Design documents from `/specs/001-phase-iii-specs/`
**Prerequisites**: plan.md (✅), spec.md (✅), research.md (✅), data-model.md (✅), contracts/ (✅)

**Tests**: NOT REQUESTED - Spec does not explicitly request TDD approach. Testing strategy defined in plan.md.
**Organization**: Tasks grouped by user story (US1-US5) to enable independent implementation.

## Format: [ID] [P?] [Story] Description
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User story label (US1-US5)
- **Paths**: Absolute from repository root (backend/src/, frontend/src/)

---

## Phase 1: Setup (4 tasks)

- [ ] T001 Create .env file in backend/ with OpenRouter API config (OPENAI_API_KEY, OPENROUTER_BASE_URL, AGENT_MODEL, FALLBACK_MODEL)
- [ ] T002 [P] Install backend deps: pip install openai mcp sse-starlette (update requirements.txt)
- [ ] T003 [P] Install frontend deps: npm install eventsource-polyfill (update package.json)
- [ ] T004 [P] Configure CORS in backend/src/main.py for SSE from localhost:3000

---

## Phase 2: Foundational - BLOCKS ALL USER STORIES (14 tasks)

- [ ] T005 Create migration backend/src/migrations/001_create_conversations.sql (id, user_id FK, created_at, updated_at)
- [ ] T006 [P] Create migration backend/src/migrations/002_create_messages.sql (id, conversation_id FK, role, content, created_at)
- [ ] T007 Run migrations on backend/todo_app.db
- [ ] T008 [P] Create Conversation model in backend/src/models/conversation.py (SQLModel, relationships)
- [ ] T009 [P] Create Message model in backend/src/models/message.py (SQLModel, role enum, relationships)
- [ ] T010 Update backend/src/models/__init__.py to export Conversation, Message
- [ ] T011 Create ConversationService in backend/src/services/conversation_service.py (get_or_create_conversation, add_message, get_conversation_context)
- [ ] T012 [P] Create MCP tools in backend/src/services/mcp_server.py: create_task, list_tasks, update_task_status, delete_task, find_tasks_by_name
- [ ] T013 Create intent detector in backend/src/services/intent_detector.py (keyword regex + LLM fallback)
- [ ] T014 Create AgentService in backend/src/services/agent_service.py (OpenRouter client, process_message method)
- [ ] T015 Create AI chat API in backend/src/api/v1/ai_chat.py (POST /chat endpoint)
- [ ] T016 [P] Create SSE endpoint in backend/src/api/v1/sse.py (GET /tasks, event streams)
- [ ] T017 Register routers in backend/src/main.py (/api/v1/ai, /api/v1/sse)
- [ ] T018 [P] Create SSE service in frontend/src/services/sseService.ts (useTaskSSE hook, event listeners)

**Checkpoint**: Foundation complete - user stories can begin

---

## Phase 3: User Story 1 - Create Task via NL (P1 MVP) (15 tasks)

**Goal**: AI-powered task creation with keyword triggers
**Test**: Login, type "add task buy groceries", verify task in dashboard <1s

- [ ] T019 [P] [US1] Implement create_task MCP tool in backend/src/services/mcp_server.py (XSS sanitization, validation)
- [ ] T020 [P] [US1] Add CREATE_TASK intent patterns to backend/src/services/intent_detector.py (regex for add|create|make)
- [ ] T021 [US1] Integrate create_task into AgentService.process_message (detect intent, call tool, format response)
- [ ] T022 [US1] Add SSE broadcast for TASK_CREATED in create_task MCP tool
- [ ] T023 [US1] Add conversational responses to AgentService (hello, hi, etc - no task creation)
- [ ] T024 [US1] Create ChatKit in frontend/src/app/components/Chat/ChatKit.tsx (message list, input, send)
- [ ] T025 [P] [US1] Create MessageList in frontend/src/app/components/Chat/MessageList.tsx (role-based styling)
- [ ] T026 [P] [US1] Create MessageInput in frontend/src/app/components/Chat/MessageInput.tsx (textarea, Enter key)
- [ ] T027 [US1] Create aiChatService in frontend/src/services/aiChatService.ts (sendMessage POST /api/v1/ai/chat)
- [ ] T028 [US1] Integrate ChatKit into frontend/src/app/dashboard/page.tsx
- [ ] T029 [US1] Add TASK_CREATED handler in frontend/src/services/sseService.ts (dispatch addTask, toast)
- [ ] T030 [US1] Update TaskTable in frontend/src/app/components/TaskTable/TaskTable.tsx (listen to SSE store updates)
- [ ] T031 [US1] Add input validation to MessageInput (1-2000 chars, trim, disable when empty)
- [ ] T032 [US1] Add OpenRouter API error handling to AgentService (user-friendly messages, retry)
- [ ] T033 [US1] Add empty title edge case to create_task MCP tool (reject with "Please provide a task name")

**Checkpoint**: MVP complete and testable

---

## Phase 4: User Story 2 - List Tasks (P2) (6 tasks)

- [ ] T034 [P] [US2] Implement list_tasks MCP tool in backend/src/services/mcp_server.py
- [ ] T035 [P] [US2] Add LIST_TASKS intent patterns to backend/src/services/intent_detector.py
- [ ] T036 [US2] Integrate list_tasks into AgentService (format as natural language list)
- [ ] T037 [US2] Add empty list edge case ("You have no tasks yet...")
- [ ] T038 [US2] Add user isolation validation to list_tasks
- [ ] T039 [US2] Format task list response (number, title, ID, status, timestamp)

---

## Phase 5: User Story 3 - Toggle Status (P3) (8 tasks)

- [ ] T040 [P] [US3] Implement update_task_status MCP tool
- [ ] T041 [P] [US3] Add UPDATE_STATUS intent patterns
- [ ] T042 [US3] Integrate update_task_status into AgentService
- [ ] T043 [US3] Add SSE broadcast for TASK_UPDATED
- [ ] T044 [US3] Add TASK_UPDATED handler in frontend
- [ ] T045 [US3] Add NOT_FOUND error handling
- [ ] T046 [US3] Add title immutability messaging
- [ ] T047 [US3] Add status validation (pending|completed)

---

## Phase 6: User Story 4 - Delete Task (P4) (9 tasks)

- [ ] T048 [P] [US4] Implement delete_task MCP tool
- [ ] T049 [P] [US4] Implement find_tasks_by_name MCP tool
- [ ] T050 [P] [US4] Add DELETE_TASK intent patterns
- [ ] T051 [US4] Integrate delete_task into AgentService
- [ ] T052 [US4] Implement fuzzy match disambiguation (1 match auto, 2-5 ask, 0 not found)
- [ ] T053 [US4] Add SSE broadcast for TASK_DELETED
- [ ] T054 [US4] Add TASK_DELETED handler in frontend
- [ ] T055 [US4] Add NOT_FOUND error handling
- [ ] T056 [US4] Format disambiguation response (numbered list with IDs)

---

## Phase 7: User Story 5 - Real-Time Sync (P2) (8 tasks)

- [ ] T057 [P] [US5] Implement SSE event queues in backend/src/api/v1/sse.py
- [ ] T058 [P] [US5] Implement broadcast_task_event function
- [ ] T059 [US5] Add connection lifecycle handling in frontend SSE service
- [ ] T060 [US5] Implement SSE reconnection logic
- [ ] T061 [US5] Add full task list resync on reconnect
- [ ] T062 [US5] Add connection status indicator to dashboard
- [ ] T063 [US5] Add HEARTBEAT event (30s interval)
- [ ] T064 [US5] Optimize event payload size (<1KB)

---

## Phase 8: Polish (16 tasks)

- [ ] T065 [P] Add rate limiting (60 req/min) to AI chat endpoint
- [ ] T066 [P] Add OpenRouter retry logic (exponential backoff, max 3)
- [ ] T067 [P] Add XSS sanitization to task titles
- [ ] T068 [P] Add title length validation (>500 chars)
- [ ] T069 [P] Add concurrent operations handling
- [ ] T070 [P] Add timezone handling (UTC storage, local display)
- [ ] T071 [P] Add auth expiry handling in ChatKit
- [ ] T072 [P] Add logging for MCP operations
- [ ] T073 [P] Add error boundary to ChatKit
- [ ] T074 [P] Add loading states to ChatKit
- [ ] T075 [P] Update backend README with Phase III setup
- [ ] T076 [P] Update frontend README with SSE notes
- [ ] T077 Run quickstart.md validation (<10 min setup)
- [ ] T078 [P] Enforce 10-message context limit in ConversationService
- [ ] T079 [P] Validate Phase II backward compatibility
- [ ] T080 Performance profiling (OpenRouter <3s p90, SSE <1s)

---

## Summary

**Total**: 80 tasks | **Parallelizable**: 48 tasks (60%)
**MVP**: T001-T033 (33 tasks = Setup + Foundational + User Story 1)
**Estimated Time**: 31-41 hours sequential, 15-20 hours with 4 developers

**Independent Test Criteria per Story**:
- US1: "add task buy groceries" → task in dashboard <1s ✅
- US2: "show tasks" → formatted list with user isolation ✅
- US3: "mark task X completed" → status updates, dashboard syncs ✅
- US4: "delete meeting" → disambiguation if 2+ matches ✅
- US5: Side-by-side chat+dashboard → updates <1s without refresh ✅

**Next**: Execute MVP (T001-T033) via Claude Code
