# Full-Stack Todo App - Complete Deployment Guide

## 📋 Project Overview

**Frontend:** Next.js 13 (App Router)
- **GitHub:** https://github.com/Shuaibali0786/full-stack-todo-app-phase-III.git
- **Production:** Deploy to Vercel
- **Local Dev:** http://localhost:3000

**Backend:** FastAPI + Python
- **Production:** HuggingFace Spaces (https://shuaibali-todo-backend-3.hf.space/)
- **Local Dev:** http://localhost:8000

**Database:** Neon PostgreSQL
- **Production DB:** `postgresql://neondb_owner:npg_B3C4FxcwJYGW@ep-jolly-wind-ainmmnu6-pooler.c-4.us-east-1.aws.neon.tech/neondb`
- **Pooled Connection:** Available for concurrent requests
- **SSL:** Required for production connections

---

## 🚀 Quick Start - Local Development

### 1. Backend Setup

```bash
cd backend

# Create/activate virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (backend/.env already configured)
# DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_B3C4FxcwJYGW@ep-jolly-wind-ainmmnu6-pooler.c-4.us-east-1.aws.neon.tech/neondb

# Start server
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend running at: http://localhost:8000
📖 API Docs at: http://localhost:8000/docs

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment (frontend/.env.local already configured)
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Start development server
npm run dev
```

✅ Frontend running at: http://localhost:3000

### 3. Test Locally

1. Open http://localhost:3000
2. Register/Login
3. Navigate to Dashboard
4. Verify:
   - ✅ Tasks load
   - ✅ Priorities load
   - ✅ Tags load
   - ✅ Can create new tasks
   - ✅ Can edit/delete tasks
   - ✅ AI chat works (with OpenRouter key)

---

## 🌐 Production Deployment

### Part 1: Deploy Backend to HuggingFace Spaces

#### A. Prepare Backend Files

1. **Create `requirements.txt`** (in `backend/` directory):
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlmodel==0.0.14
asyncpg==0.29.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
python-dotenv==1.0.0
httpx==0.25.2
```

2. **Create `Dockerfile`** (in `backend/` directory):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 7860

# Run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860"]
```

3. **Create `.env` for HuggingFace** (will be set in Space settings):
```env
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_B3C4FxcwJYGW@ep-jolly-wind-ainmmnu6-pooler.c-4.us-east-1.aws.neon.tech/neondb
SECRET_KEY=your-production-secret-key-here-use-strong-random-string
OPENAI_API_KEY=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
AGENT_MODEL=anthropic/claude-3.5-sonnet
RATE_LIMIT_PER_MINUTE=100
```

#### B. Deploy to HuggingFace

1. **Push to GitHub:**
```bash
cd backend
git add .
git commit -m "Prepare backend for HuggingFace deployment"
git push origin main
```

2. **Create HuggingFace Space:**
   - Go to https://huggingface.co/spaces
   - Click "Create new Space"
   - Name: `todo-backend-3` (or your preferred name)
   - SDK: **Docker**
   - Visibility: Public or Private

3. **Connect GitHub:**
   - In Space settings, connect your GitHub repo
   - Point to `backend/` directory
   - Set environment variables in Space settings:
     - `DATABASE_URL`
     - `SECRET_KEY`
     - `OPENAI_API_KEY`
     - `AGENT_MODEL`

4. **Wait for Build:**
   - HuggingFace will build and deploy automatically
   - Check logs for any errors
   - Space URL: `https://USERNAME-SPACENAME.hf.space/`

5. **Test Deployed Backend:**
```bash
# Test health endpoint
curl https://shuaibali-todo-backend-3.hf.space/health

# Should return: {"status":"healthy","service":"todo-api"}
```

#### C. Update CORS for Production

If you get CORS errors, update `backend/src/main.py`:

```python
# Update CORS to include your Vercel domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-app.vercel.app",  # Add your Vercel URL
        "*"  # Remove in production for security
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Part 2: Deploy Frontend to Vercel

#### A. Update Frontend for Production

1. **Update `frontend/.env.production`:**
```env
# Production environment (used by Vercel)
NEXT_PUBLIC_API_URL=https://shuaibali-todo-backend-3.hf.space
```

2. **Verify Build Works:**
```bash
cd frontend
npm run build
```

If build succeeds, you're ready to deploy!

#### B. Deploy to Vercel

##### Option 1: Via Vercel Dashboard (Recommended)

1. **Go to Vercel:** https://vercel.com/
2. **Import Project:**
   - Click "Add New" → "Project"
   - Import from GitHub
   - Select your repository
3. **Configure:**
   - Framework Preset: **Next.js**
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`
4. **Environment Variables:**
   - Add: `NEXT_PUBLIC_API_URL` = `https://shuaibali-todo-backend-3.hf.space`
5. **Deploy:**
   - Click "Deploy"
   - Wait for build to complete

##### Option 2: Via Vercel CLI

```bash
cd frontend

# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name: full-stack-todo-app
# - Directory: ./
# - Override settings? No

# Set environment variable
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://shuaibali-todo-backend-3.hf.space

# Deploy to production
vercel --prod
```

6. **Your App URL:**
   - Vercel will provide: `https://your-app.vercel.app`

---

## 🔧 Environment Variables Reference

### Backend `.env` (Local Development)

```env
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_B3C4FxcwJYGW@ep-jolly-wind-ainmmnu6-pooler.c-4.us-east-1.aws.neon.tech/neondb
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
BETTER_AUTH_SECRET=your-better-auth-secret-change-in-production
OPENAI_API_KEY=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
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
AGENT_MODEL=anthropic/claude-3.5-sonnet
FALLBACK_MODEL=anthropic/claude-3.5-sonnet
RATE_LIMIT_PER_MINUTE=100
```

### Frontend `.env.local` (Local Development)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Frontend `.env.production` (Production/Vercel)

```env
NEXT_PUBLIC_API_URL=https://shuaibali-todo-backend-3.hf.space
```

---

## 🧪 Testing Checklist

### Local Testing

- [ ] Backend starts without errors
- [ ] Backend connects to Neon DB
- [ ] Frontend starts without errors
- [ ] Can register new user
- [ ] Can login
- [ ] Dashboard loads tasks
- [ ] Can create new task
- [ ] Can edit task
- [ ] Can delete task
- [ ] Priorities and tags load
- [ ] AI chat works
- [ ] No console errors

### Production Testing

- [ ] HuggingFace backend is accessible
- [ ] Backend health check returns 200 OK
- [ ] Vercel frontend is accessible
- [ ] Frontend connects to HuggingFace backend
- [ ] All features work as in local
- [ ] No CORS errors
- [ ] Authentication works
- [ ] Tasks persist in Neon DB

---

## 🐛 Troubleshooting

### Backend Issues

#### Cannot connect to Neon DB
**Error:** `asyncpg.exceptions.InvalidAuthorizationSpecificationError`

**Solution:**
1. Verify DATABASE_URL format:
   ```
   postgresql+asyncpg://user:password@host/dbname
   ```
2. Check Neon console for correct credentials
3. Ensure IP is not blocked in Neon settings

#### 422 Errors on GET requests
**Cause:** Invalid query parameters or authentication issue

**Solution:**
1. Check if JWT token is valid
2. Verify all query parameters are optional with defaults
3. Check backend logs for validation errors

#### 405 Method Not Allowed
**Cause:** Route decorator missing (e.g., `@router.post("")`)

**Solution:** Already fixed! Both decorators exist:
```python
@router.post("/", response_model=TaskResponse)
@router.post("", response_model=TaskResponse)
```

### Frontend Issues

#### API calls fail with CORS error
**Solution:** Update backend CORS settings to include frontend URL

#### Tasks don't load
**Solution:**
1. Check `NEXT_PUBLIC_API_URL` is correct
2. Verify backend is accessible
3. Check browser console for errors
4. Verify JWT token exists: `localStorage.getItem('access_token')`

#### Build fails on Vercel
**Solution:**
1. Check build logs for specific errors
2. Ensure all dependencies in `package.json`
3. Verify no TypeScript errors
4. Test `npm run build` locally first

---

## 📊 Architecture Diagram

```
┌─────────────────┐
│   Vercel        │
│   (Frontend)    │
│   Next.js 13    │
│   Port: 443     │
└────────┬────────┘
         │ HTTPS
         │ NEXT_PUBLIC_API_URL
         │
         ▼
┌─────────────────┐
│  HuggingFace    │
│  (Backend)      │
│  FastAPI        │
│  Port: 7860     │
└────────┬────────┘
         │ PostgreSQL
         │ DATABASE_URL
         │
         ▼
┌─────────────────┐
│  Neon           │
│  PostgreSQL     │
│  (Database)     │
│  Port: 5432     │
└─────────────────┘
```

---

## 🔐 Security Checklist

- [ ] Change `SECRET_KEY` to strong random string in production
- [ ] Use environment variables for all secrets
- [ ] Enable SSL for database connections
- [ ] Set strong CORS policy (don't use `allow_origins=["*"]` in production)
- [ ] Use HTTPS for all API calls
- [ ] Keep JWT tokens short-lived (15-30 minutes)
- [ ] Store refresh tokens securely
- [ ] Rate limit API endpoints
- [ ] Validate all user inputs
- [ ] Use prepared statements for DB queries (SQLModel does this)

---

## 📝 Common Commands

### Backend
```bash
# Start dev server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Run migrations (if using Alembic)
alembic upgrade head

# Seed database
python -c "from src.core.seed_data import seed_default_data; seed_default_data()"

# Test API endpoint
curl http://localhost:8000/health
```

### Frontend
```bash
# Install dependencies
npm install

# Dev server
npm run dev

# Build for production
npm run build

# Start production server locally
npm start

# Lint
npm run lint
```

### Git
```bash
# Commit changes
git add .
git commit -m "Your message"
git push origin main

# Create new branch
git checkout -b feature/your-feature

# Merge branch
git checkout main
git merge feature/your-feature
```

---

## 🎉 Success Criteria

Your deployment is successful when:

1. ✅ Backend on HuggingFace returns 200 OK on `/health`
2. ✅ Frontend on Vercel loads without errors
3. ✅ Can register and login
4. ✅ Dashboard displays tasks from Neon DB
5. ✅ Can perform all CRUD operations on tasks
6. ✅ AI chat functionality works
7. ✅ No CORS or authentication errors
8. ✅ Data persists in Neon PostgreSQL
9. ✅ Application is accessible publicly

---

## 📚 Additional Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Next.js Docs:** https://nextjs.org/docs
- **Vercel Deployment:** https://vercel.com/docs
- **HuggingFace Spaces:** https://huggingface.co/docs/hub/spaces
- **Neon Database:** https://neon.tech/docs
- **SQLModel:** https://sqlmodel.tiangolo.com/

---

**Need Help?** Check the troubleshooting section or review the error logs from:
- Backend: Check HuggingFace Space logs
- Frontend: Check Vercel deployment logs
- Database: Check Neon dashboard for connection issues
