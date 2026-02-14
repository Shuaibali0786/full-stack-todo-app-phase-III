---
id: 10
title: Remove HuggingFace Force Localhost Only
stage: general
date: 2026-02-14
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: Dell 5500
command: "Remove HuggingFace backend usage, force localhost"
labels: ["api", "cors", "auth", "localhost", "bugfix"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/src/utils/api.ts
  - frontend/vercel.json (deleted)
  - frontend/.env.production
  - backend/src/main.py
  - backend/src/api/v1/auth.py
tests:
  - none
---

## Prompt

I want to completely remove HuggingFace backend usage.

My project must run ONLY on localhost.

1) REMOVE HUGGINGFACE COMPLETELY
- Remove ALL references to: https://shuaibali-todo-backend.hf.space
- Delete: vercel.json, any production rewrites, any proxy configs, any NEXT_PUBLIC_API_URL that points to HuggingFace
- Remove all environment-based API switching logic.

2) FORCE FRONTEND TO USE LOCALHOST
In src/utils/api.ts replace base URL logic with:
    const API_BASE_URL = "http://localhost:8000";
Do NOT use process.env, relative paths, or Vercel rewrites.

3) FIX AUTH REGISTER 500 ERROR
Currently getting: AxiosError: 500 at authApi.register(userData)
Ensure duplicate email returns 400 with proper message. Do NOT crash server.

4) FIX ROUTE ORDER (UUID ERROR PREVENTION)
Ensure dynamic routes like /{task_id} are ALWAYS at the bottom.

5) FIX CORS
Allow: http://localhost:3000

## Response snapshot

Applied 5 targeted changes:
1. `frontend/src/utils/api.ts`: Added `const API_BASE_URL = "http://localhost:8000"` and replaced both `process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'` occurrences with `API_BASE_URL`.
2. `frontend/vercel.json`: Deleted (contained `NEXT_PUBLIC_API_URL=https://shuaibali-todo-backend.hf.space`).
3. `frontend/.env.production`: Overwrote — removed HuggingFace URL, kept only `NODE_ENV=production`.
4. `backend/src/main.py`: Changed `allow_origins=["*"]` to `allow_origins=["http://localhost:3000"]`.
5. `backend/src/api/v1/auth.py`: Imported `IntegrityError`, added specific catch before `SQLAlchemyError` to return HTTP 400 on duplicate email (also catches race conditions at DB level). Changed `ValueError` → 409 to 400 for consistency.

Route order in `tasks.py` was already correct (static routes before `/{task_id}`).

## Outcome

- ✅ Impact: Frontend always calls http://localhost:8000; no HuggingFace references remain; CORS restricted to localhost:3000; duplicate email returns 400 not 500.
- 🧪 Tests: None run — manual verification required (register with duplicate email, check CORS headers).
- 📁 Files: 5 files modified/deleted.
- 🔁 Next prompts: Start backend with `uvicorn src.main:app --reload`, start frontend with `npm run dev`, test registration flow.
- 🧠 Reflection: Root cause of 500 was missing IntegrityError handler — DB-level unique constraint violations weren't being caught as 400.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): none
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): Add integration test for duplicate email registration endpoint
