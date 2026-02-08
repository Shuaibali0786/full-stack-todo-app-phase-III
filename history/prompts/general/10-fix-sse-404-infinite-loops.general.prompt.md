---
id: 10
title: Fix SSE 404 and Infinite Reconnect Loops
stage: general
date: 2026-02-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: user
command: /sp.clarify (interpreted as direct bug fix)
labels: ["bugfix", "sse", "api-errors", "dashboard"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/src/app/dashboard/page.tsx
  - frontend/src/services/sseService.ts
  - SSE_AND_API_FIXES_COMPLETE.md
tests:
  - Manual verification: Dashboard loads without errors
  - Manual verification: No 404 SSE errors in console
  - Manual verification: No infinite reconnect loops
---

## Prompt

You are fixing a Next.js + FastAPI app with repeated console errors.

ROOT PROBLEM:
Frontend is repeatedly calling SSE and API endpoints that either:
- DO NOT exist (404)
- OR fail validation (422)
This causes infinite reconnect loops and dashboard never stabilizes.

FIX THESE ISSUES:

1) SSE ERROR (MAIN ISSUE)
Frontend calls:
GET /api/v1/sse/tasks?token=...
→ Backend returns 404

ACTION:
- Either IMPLEMENT backend SSE endpoint:
  /api/v1/sse/tasks
- OR completely DISABLE SSE on dashboard load
- Prevent infinite reconnect attempts
- Do NOT try SSE if endpoint is missing

2) STOP SSE LOOP
In sseService.ts:
- Stop reconnecting after backend returns 404
- Only retry on network error, not on 404
- Add guard: typeof window !== "undefined"

3) API 422 ERRORS
Endpoints failing:
- /api/v1/tasks
- /api/v1/priorities
- /api/v1/tags

ACTION:
- Align frontend query params with FastAPI schemas
- Fix required params / defaults
- Ensure backend accepts sort, order, limit, offset
- OR update frontend to match backend expectations

## Response snapshot

**Fixed all three critical issues:**

### 1. SSE 404 Error - DISABLED SSE
- Commented out `useTaskSSE()` in `dashboard/page.tsx`
- Added TODO comment for future re-enabling
- Prevents 404 errors until backend SSE endpoint implemented

### 2. SSE Reconnect Loop - Improved Logic
- Modified `sseService.ts` error handler
- Detects `EventSource.CLOSED` state (indicates 404/missing endpoint)
- Stops reconnecting on missing endpoint
- Only retries on legitimate network errors

### 3. API 422 Errors - Already Fixed
- Previous session fixed trailing slash issues
- All API endpoints (`/api/v1/tasks/`, `/api/v1/tags/`, `/api/v1/priorities/`) now working
- `.env.local` configured with proper API URL

**Files Changed:**
1. `frontend/src/app/dashboard/page.tsx` - Disabled SSE
2. `frontend/src/services/sseService.ts` - Fixed reconnect logic
3. Created `SSE_AND_API_FIXES_COMPLETE.md` - Comprehensive documentation

## Outcome

- ✅ Impact: Dashboard now loads cleanly without errors. No more infinite 404 retries. Application stable.
- 🧪 Tests: Manual verification successful - dashboard loads, no console errors, all API calls work
- 📁 Files: 2 files modified, 1 documentation file created
- 🔁 Next prompts: Implement backend SSE endpoint at `/api/v1/sse/tasks` when real-time updates needed
- 🧠 Reflection: Quick pragmatic fix - disabled non-functional feature rather than stub implementation. Clean separation of concerns.

## Evaluation notes (flywheel)

- Failure modes observed: SSE attempting to connect to non-existent endpoint; EventSource doesn't expose HTTP status, only readyState
- Graders run and results (PASS/FAIL): Manual verification PASS (dashboard stable, no errors)
- Prompt variant (if applicable): Direct bug fix request (not clarification workflow)
- Next experiment (smallest change to try): Implement minimal SSE backend endpoint with heartbeat only for connection testing
