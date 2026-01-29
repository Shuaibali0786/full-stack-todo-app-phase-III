# Quickstart Guide: TaskFlow AI Development Setup

**Feature**: TaskFlow AI - Intelligent Task Assistant
**Date**: 2026-01-27
**Phase**: Phase 1 (Design)
**Target**: Developers setting up local environment for Phase III implementation

---

## Overview

This guide enables developers to set up a complete TaskFlow AI development environment in **under 10 minutes**. It covers backend (FastAPI + OpenRouter), frontend (Next.js + Chat UI), database (SQLite), and real-time sync (SSE).

**Prerequisites**:
- ✅ Phase II application functional (backend + frontend + database)
- ✅ Python 3.11+, Node.js 18+, npm/yarn
- ✅ OpenRouter API key ([get one here](https://openrouter.ai/keys))

---

## Step 1: Environment Configuration (2 minutes)

### 1.1 Create `.env` file in `backend/` directory

```bash
cd backend
cp .env.example .env  # If exists, otherwise create new
```

### 1.2 Add OpenRouter API configuration

```bash
# backend/.env

# Existing Phase II config (leave unchanged)
DATABASE_URL=sqlite:///./todo_app.db
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
BETTER_AUTH_SECRET=your-better-auth-secret

# Phase III: OpenRouter API Configuration (NEW)
OPENAI_API_KEY=sk-or-v1-YOUR_OPENROUTER_API_KEY_HERE  # ⚠️ REQUIRED
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
AGENT_MODEL=anthropic/claude-3.5-sonnet  # Primary model
FALLBACK_MODEL=openai/gpt-4-turbo        # Fallback if Claude unavailable
RATE_LIMIT_PER_MINUTE=60                  # OpenRouter free tier limit
```

**📝 Notes**:
- Replace `YOUR_OPENROUTER_API_KEY_HERE` with your actual OpenRouter API key
- Free tier: 60 requests/minute (sufficient for development)
- Paid tier recommended for production: https://openrouter.ai/docs#limits

---

## Step 2: Install Phase III Dependencies (3 minutes)

### 2.1 Backend Dependencies

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Phase III specific packages (if not in requirements.txt):
pip install openai  # OpenRouter client (compatible with OpenAI SDK)
pip install mcp     # Official MCP SDK
pip install sse-starlette  # Server-Sent Events for FastAPI
```

### 2.2 Frontend Dependencies

```bash
cd frontend

# Install Node.js dependencies
npm install  # or yarn install

# Phase III specific packages (if not in package.json):
npm install @openai/chatkit  # OpenAI ChatKit UI components (optional)
npm install eventsource-polyfill  # SSE support for older browsers
```

### 2.3 Verify Installation

```bash
# Backend
cd backend
python -c "import openai, mcp; print('Backend dependencies OK')"

# Frontend
cd frontend
npm list @openai/chatkit eventsource-polyfill  # Should not error
```

---

## Step 3: Database Migration (1 minute)

### 3.1 Run Phase III Migrations

```bash
cd backend

# Apply migrations (creates conversations and messages tables)
python -m alembic upgrade head

# Or manually run SQL (if Alembic not configured):
sqlite3 todo_app.db < src/migrations/001_create_conversations.sql
sqlite3 todo_app.db < src/migrations/002_create_messages.sql
```

### 3.2 Verify Schema

```bash
sqlite3 todo_app.db

# Run in SQLite shell:
.tables  # Should show: users, tasks, priorities, conversations, messages
.schema conversations  # Should show id, user_id, created_at, updated_at
.schema messages       # Should show id, conversation_id, role, content, created_at
.exit
```

**✅ Success Indicator**: Tables `conversations` and `messages` exist in database

---

## Step 4: Start Development Servers (2 minutes)

### 4.1 Start Backend (Terminal 1)

```bash
cd backend

# Development mode with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete.
```

### 4.2 Start Frontend (Terminal 2)

```bash
cd frontend

# Development mode
npm run dev  # or yarn dev

# Expected output:
# ▲ Next.js 14.x.x
# - Local:   http://localhost:3000
# ✓ Ready in Xms
```

### 4.3 Verify Services

Open browser and check:
- ✅ Backend health: http://localhost:8000/docs (FastAPI Swagger UI)
- ✅ Frontend: http://localhost:3000 (Login page or dashboard if authenticated)
- ✅ Phase II endpoints: http://localhost:8000/api/v1/tasks (should require auth)

---

## Step 5: Test OpenRouter Integration (1 minute)

### 5.1 Run Test Script

```bash
cd backend

# Test OpenRouter API connection
python test_openrouter.py

# Expected output:
# ✅ OpenRouter API connected
# Model: anthropic/claude-3.5-sonnet
# Response: [AI-generated text]
```

### 5.2 Troubleshooting

| Error | Solution |
|-------|----------|
| `401 Unauthorized` | Verify `OPENAI_API_KEY` in `.env` is correct (starts with `sk-or-v1-`) |
| `429 Rate Limit` | Wait 60 seconds (free tier limit), or upgrade to paid tier |
| `Connection timeout` | Check internet connection, OpenRouter may be down (status: https://status.openrouter.ai) |

---

## Step 6: Verify Phase III Endpoints (1 minute)

### 6.1 Test AI Chat API (Authenticated Request)

```bash
# 1. Login to get JWT token (use existing Phase II user or register new)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# Response: {"access_token": "eyJ...", "token_type": "bearer"}

# 2. Send AI chat message
export TOKEN="eyJ..."  # Replace with actual token from step 1
curl -X POST http://localhost:8000/api/v1/ai/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "add task buy groceries"}'

# Expected response:
# {
#   "response": "✅ Task created: 'buy groceries' (ID: abc-123, Status: pending)",
#   "actions": [
#     {
#       "type": "TASK_CREATED",
#       "task": {
#         "id": "abc-123",
#         "title": "buy groceries",
#         "status": "pending",
#         "created_at": "2026-01-27T10:30:00Z"
#       }
#     }
#   ]
# }
```

### 6.2 Test SSE Endpoint (Real-Time Sync)

```bash
# Open SSE stream (keep this running)
curl -N http://localhost:8000/api/v1/sse/tasks \
  -H "Authorization: Bearer $TOKEN"

# In another terminal, create a task via AI chat (use curl from 6.1)
# Expected SSE event:
# event: TASK_CREATED
# data: {"task": {"id": "abc-123", "title": "buy groceries", "status": "pending", "created_at": "2026-01-27T10:30:00Z"}}
```

---

## Development Workflow

### Typical Development Session

1. **Start servers** (Step 4)
2. **Open browser**: http://localhost:3000 → Login → Dashboard
3. **Open developer tools**: Console + Network tabs
4. **Test AI chat**: Type "add task test" in chat interface
5. **Verify dashboard update**: New task appears instantly (SSE event)

### Hot Reload

- **Backend**: Uvicorn auto-reloads on `.py` file changes
- **Frontend**: Next.js auto-reloads on `.tsx`/`.ts` file changes

### Debugging

```bash
# Backend logs (in terminal 1)
# Shows API requests, database queries, OpenRouter API calls

# Frontend console (in browser DevTools)
# Shows SSE events, React component renders, API responses

# Database inspection
sqlite3 backend/todo_app.db
SELECT * FROM conversations;
SELECT * FROM messages ORDER BY created_at DESC LIMIT 10;
```

---

## Common Issues & Solutions

### Issue 1: "OpenRouter API key not configured"
**Cause**: Missing or incorrect `OPENAI_API_KEY` in `.env`
**Solution**:
```bash
cd backend
grep OPENAI_API_KEY .env  # Should show sk-or-v1-...
# If missing, add it and restart backend server
```

### Issue 2: "SSE events not received in frontend"
**Cause**: SSE connection not established or CORS issue
**Solution**:
```bash
# Check browser console for SSE errors
# Verify backend logs show: "SSE connection established for user X"
# Check CORS settings in backend/src/main.py (allow localhost:3000)
```

### Issue 3: "Task created but dashboard not updating"
**Cause**: SSE stream not connected or event broadcasting disabled
**Solution**:
```bash
# 1. Check if SSE endpoint returns events (curl test from 6.2)
# 2. Verify frontend useTaskSSE hook is mounted
# 3. Check backend broadcast_task_event() is called in MCP tools
```

### Issue 4: "Database schema mismatch"
**Cause**: Migrations not applied or old database file
**Solution**:
```bash
cd backend
rm todo_app.db  # ⚠️ WARNING: Deletes all data
python -m alembic upgrade head  # Recreate with Phase III schema
# Or: manually run migration SQL files
```

### Issue 5: "Import errors (ModuleNotFoundError)"
**Cause**: Dependencies not installed or virtual environment not activated
**Solution**:
```bash
cd backend
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

---

## Testing Strategy

### Manual Testing Checklist

- [ ] **Task Creation**: "add task X" → Dashboard shows new task instantly
- [ ] **Task Listing**: "show tasks" → AI lists all tasks with IDs and status
- [ ] **Status Toggle**: "mark X as completed" → Dashboard updates status
- [ ] **Task Deletion**: "delete X" → Task disappears from dashboard
- [ ] **Disambiguation**: "delete meeting" (multiple matches) → AI asks for clarification
- [ ] **Conversational**: "hello" → AI responds without creating task
- [ ] **User Isolation**: Login as User A, create task → Login as User B, task not visible

### Automated Testing

```bash
# Backend unit tests
cd backend
pytest tests/unit/test_mcp_tools.py -v
pytest tests/unit/test_agent_service.py -v

# Backend integration tests
pytest tests/integration/test_ai_chat_flow.py -v

# Backend E2E tests
pytest tests/e2e/test_ai_chat_api.py -v

# Frontend tests
cd frontend
npm test -- --coverage
```

---

## Next Steps

1. **Read Spec**: Review `specs/001-phase-iii-specs/spec.md` for functional requirements
2. **Read Plan**: Review `specs/001-phase-iii-specs/plan.md` for architecture decisions
3. **Read Contracts**: Review API contracts in `specs/001-phase-iii-specs/contracts/`
4. **Implement Tasks**: Run `/sp.tasks` to generate implementation task list
5. **Execute via Claude Code**: Use Claude Code to implement tasks from `tasks.md`

---

## Resources

- **OpenRouter Docs**: https://openrouter.ai/docs
- **MCP Specification**: https://spec.modelcontextprotocol.io/
- **FastAPI SSE Guide**: https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse
- **React EventSource**: https://developer.mozilla.org/en-US/docs/Web/API/EventSource

---

**Setup Time Target**: <10 minutes
**Success Criteria**: AI chat responds to "add task test" and dashboard updates in real-time

**Support**: If stuck, check `specs/001-phase-iii-specs/plan.md` → Risks & Mitigations section
