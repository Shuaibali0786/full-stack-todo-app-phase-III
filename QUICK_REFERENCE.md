# 🚀 Quick Reference Card

## Start Development (Local)

### Backend
```bash
cd backend
venv\Scripts\activate
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```
**Running at:** http://localhost:8000
**API Docs:** http://localhost:8000/docs

### Frontend
```bash
cd frontend
npm run dev
```
**Running at:** http://localhost:3000

---

## Environment Variables

### Backend `.env`
```env
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_B3C4FxcwJYGW@ep-jolly-wind-ainmmnu6-pooler.c-4.us-east-1.aws.neon.tech/neondb
OPENAI_API_KEY=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
AGENT_MODEL=anthropic/claude-3.5-sonnet
SECRET_KEY=your-super-secret-key
```

### Frontend `.env.local` (Development)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Frontend `.env.production` (Vercel)
```env
NEXT_PUBLIC_API_URL=https://shuaibali-todo-backend-3.hf.space
```

---

## URLs

| Service | URL |
|---------|-----|
| Frontend (Local) | http://localhost:3000 |
| Backend (Local) | http://localhost:8000 |
| Backend (HuggingFace) | https://shuaibali-todo-backend-3.hf.space |
| Neon Database | ep-jolly-wind-ainmmnu6-pooler.c-4.us-east-1.aws.neon.tech |
| GitHub Repo | https://github.com/Shuaibali0786/full-stack-todo-app-phase-III.git |

---

## Key Files

### Created
- `frontend/src/lib/cn.ts` - ✅ Tailwind utility
- `frontend/src/lib/animations.ts` - ✅ Framer Motion animations
- `backend/Dockerfile` - ✅ HuggingFace deployment
- `backend/.env` - ✅ Environment config
- `frontend/.env.local` - ✅ Local config
- `frontend/.env.production` - ✅ Production config

### Updated
- `backend/src/api/v1/tasks.py` - ✅ Added POST ""
- `backend/src/api/v1/priorities.py` - ✅ Added POST ""
- `backend/src/api/v1/tags.py` - ✅ Added POST ""
- `backend/src/main.py` - ✅ Fixed router prefixes
- `backend/src/api/main.py` - ✅ Fixed router prefixes

---

## API Endpoints

### Authentication
```
POST /api/v1/login
POST /api/v1/register
POST /api/v1/refresh
```

### Tasks
```
GET    /api/v1/tasks           # List all
POST   /api/v1/tasks           # Create
GET    /api/v1/tasks/{id}      # Get one
PUT    /api/v1/tasks/{id}      # Update
DELETE /api/v1/tasks/{id}      # Delete
PATCH  /api/v1/tasks/{id}/complete
```

### Metadata
```
GET    /api/v1/priorities
POST   /api/v1/priorities
GET    /api/v1/tags
POST   /api/v1/tags
```

---

## Test Commands

### Test Backend Health
```bash
curl http://localhost:8000/health
curl https://shuaibali-todo-backend-3.hf.space/health
```

### Test with Authentication
```bash
# Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}' \
  | jq -r '.access_token')

# Get tasks
curl http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN"
```

---

## Common Issues & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| 405 Method Not Allowed | POST route missing | ✅ FIXED - Added `@router.post("")` |
| 422 Unprocessable Entity | Auth issue / Invalid params | Check JWT token, verify params |
| Module not found: @/lib/cn | Missing utility file | ✅ FIXED - Created cn.ts |
| CORS error | Backend not allowing origin | Update CORS in main.py |
| Cannot connect to DB | Wrong DATABASE_URL | ✅ FIXED - Using correct Neon URL |

---

## Deployment

### HuggingFace (Backend)
1. Push code to GitHub
2. Create Docker Space on HuggingFace
3. Connect GitHub repo
4. Set environment variables
5. Deploy

**Current:** https://shuaibali-todo-backend-3.hf.space

### Vercel (Frontend)
1. Push code to GitHub
2. Import project in Vercel
3. Set root directory: `frontend`
4. Add env: `NEXT_PUBLIC_API_URL`
5. Deploy

---

## Project Structure

```
full-stack-todo-app-phase-III/
├── backend/
│   ├── src/
│   │   ├── api/v1/         # API routes
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   ├── core/           # Config & security
│   │   └── main.py         # Entry point
│   ├── .env                # ✅ Environment config
│   ├── Dockerfile          # ✅ HuggingFace deploy
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── app/            # Next.js pages
│   │   ├── components/     # React components
│   │   ├── lib/            # ✅ Utilities (cn, animations)
│   │   └── utils/          # API client
│   ├── .env.local          # ✅ Local dev
│   ├── .env.production     # ✅ Production
│   └── package.json
│
└── DEPLOYMENT_GUIDE.md     # ✅ Complete guide
```

---

## Success Checklist

- [x] Backend connects to Neon DB
- [x] All API endpoints work (no 405/422)
- [x] Frontend imports fixed
- [x] Environment variables configured
- [x] Local development works
- [x] Deployment files ready
- [x] Documentation complete

---

## Documentation Files

1. **COMPLETE_FIX_SUMMARY.md** - Detailed fix summary
2. **DEPLOYMENT_GUIDE.md** - Step-by-step deployment
3. **API_FIX_SUMMARY.md** - Technical API details
4. **QUICK_START_GUIDE.md** - Quick start instructions
5. **QUICK_REFERENCE.md** - This file!

---

## Get Help

**Documentation:**
- Read: `DEPLOYMENT_GUIDE.md`
- API Details: `API_FIX_SUMMARY.md`
- Quick Start: `QUICK_START_GUIDE.md`

**Resources:**
- FastAPI: https://fastapi.tiangolo.com/
- Next.js: https://nextjs.org/docs
- Neon: https://neon.tech/docs
- HuggingFace: https://huggingface.co/docs/hub/spaces
- Vercel: https://vercel.com/docs

---

**Last Updated:** 2026-02-08
**Status:** ✅ All Systems Ready
