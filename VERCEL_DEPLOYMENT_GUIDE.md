# 🚀 Vercel Deployment Guide for Full-Stack Todo App

## 📋 Overview

This guide will help you deploy:
- **Frontend**: Next.js → Vercel
- **Backend**: FastAPI → HuggingFace Spaces (already at: https://shuaibali-todo-backend.hf.space)
- **Database**: Neon PostgreSQL (already configured)

---

## ✅ Pre-Deployment Checklist

- [x] Backend `.env` updated with new Neon database
- [x] Frontend `.env.production` configured
- [x] Dockerfile exists for backend
- [x] All dependencies installed locally
- [ ] Git repository pushed to GitHub
- [ ] Vercel account created
- [ ] HuggingFace account created

---

## 🎯 Part 1: Deploy Backend to HuggingFace Spaces

### Option A: Using Existing HuggingFace Deployment

Your backend is already deployed at: **https://shuaibali-todo-backend.hf.space**

**Update Environment Variables:**

1. Go to: https://huggingface.co/spaces
2. Find your space: `shuaibali-todo-backend`
3. Click **Settings** → **Variables and secrets**
4. Update these environment variables:

```env
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_Q2CPSxjXH1ue@ep-steep-union-ai8qcccs-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require
SECRET_KEY=prod-todo-app-secret-key-change-this-to-random-64-char-string
OPENAI_API_KEY=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
AGENT_MODEL=anthropic/claude-3.5-sonnet
RATE_LIMIT_PER_MINUTE=100
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
BETTER_AUTH_SECRET=your-better-auth-secret-change-in-production
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

5. **Trigger Rebuild**: Click **Factory reboot** to restart with new env vars

### Option B: Create New HuggingFace Space

If you want to deploy to a new space:

```bash
cd backend

# Make sure Dockerfile exists (already created)
# Push to GitHub first
git add .
git commit -m "Prepare backend for deployment"
git push origin master
```

Then:
1. Go to https://huggingface.co/new-space
2. **Space name**: `todo-backend-phase-iii`
3. **SDK**: Docker
4. **Visibility**: Public
5. **Clone from Git**: Paste your GitHub repo URL
6. **Path in repo**: `backend/`
7. Add all environment variables from above
8. Click **Create Space**

### Test Backend Deployment

```bash
# Test health endpoint
curl https://shuaibali-todo-backend.hf.space/health

# Should return:
# {"status":"healthy","service":"todo-api"}

# Test API docs
# Open in browser: https://shuaibali-todo-backend.hf.space/docs
```

---

## 🎯 Part 2: Deploy Frontend to Vercel

### Method 1: Vercel Dashboard (Recommended for First Deployment)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin master
   ```

2. **Go to Vercel:**
   - Visit: https://vercel.com/
   - Click **"Add New..."** → **"Project"**
   - Click **"Import Git Repository"**

3. **Import from GitHub:**
   - Select your repository: `full-stack-todo-app-phase-III`
   - Click **"Import"**

4. **Configure Project:**
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `frontend` ← **IMPORTANT!**
   - **Build Command**: `npm run build` (auto-filled)
   - **Output Directory**: `.next` (auto-filled)
   - **Install Command**: `npm install` (auto-filled)

5. **Environment Variables:**
   Click **"Environment Variables"** and add:

   | Name | Value |
   |------|-------|
   | `NEXT_PUBLIC_API_URL` | `https://shuaibali-todo-backend.hf.space` |
   | `NODE_ENV` | `production` |

6. **Deploy:**
   - Click **"Deploy"**
   - Wait 2-3 minutes for build
   - Your app will be live at: `https://your-app-name.vercel.app`

### Method 2: Vercel CLI (For Updates & Advanced Users)

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to frontend
cd frontend

# Login to Vercel
vercel login

# First deployment (production)
vercel --prod

# Follow the prompts:
# ✔ Set up and deploy "frontend"? [Y/n] y
# ✔ Which scope? → Your account
# ✔ Link to existing project? [y/N] n
# ✔ What's your project's name? → full-stack-todo-app-phase-iii
# ✔ In which directory is your code located? → ./

# Add environment variable
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://shuaibali-todo-backend.hf.space

# Redeploy with env vars
vercel --prod
```

### Method 3: GitHub Integration (Auto-Deploy on Push)

After initial setup via Dashboard:

1. Every push to `master` branch will auto-deploy
2. Pull requests will get preview deployments
3. Monitor deployments at: https://vercel.com/dashboard

---

## 🧪 Post-Deployment Testing

### 1. Test Backend (HuggingFace)

```bash
# Health check
curl https://shuaibali-todo-backend.hf.space/health

# Test registration
curl -X POST https://shuaibali-todo-backend.hf.space/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test1234!","name":"Test User"}'

# API docs
# https://shuaibali-todo-backend.hf.space/docs
```

### 2. Test Frontend (Vercel)

Visit your Vercel URL: `https://your-app-name.vercel.app`

**Test Checklist:**
- [ ] Homepage loads without errors
- [ ] Can navigate to login page
- [ ] Can register new account
- [ ] Can login with credentials
- [ ] Dashboard loads after login
- [ ] Tasks display correctly
- [ ] Can create new task
- [ ] Can edit existing task
- [ ] Can delete task
- [ ] Priorities dropdown works
- [ ] Tags load correctly
- [ ] AI chat works (if OpenRouter key is valid)
- [ ] No CORS errors in console
- [ ] No 422/405 errors
- [ ] Real-time updates work (SSE)

### 3. Check Browser Console

Open DevTools (F12) → Console:
- ✅ No red errors
- ✅ API calls succeed (200 status)
- ✅ Authentication headers present
- ✅ SSE connection established

### 4. Network Tab Verification

1. Open DevTools → Network tab
2. Filter: Fetch/XHR
3. Check:
   - ✅ `/api/auth/login` → 200 OK
   - ✅ `/api/tasks` → 200 OK
   - ✅ `/api/priorities` → 200 OK
   - ✅ `/api/tags` → 200 OK
   - ✅ All requests include `Authorization: Bearer ...`

---

## 🔧 Troubleshooting

### Issue 1: Build Fails on Vercel

**Error:** `Module not found` or `Cannot find module`

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build  # Test locally first
git add package-lock.json
git commit -m "Fix dependencies"
git push
```

### Issue 2: API Calls Return 404

**Cause:** `NEXT_PUBLIC_API_URL` not set or incorrect

**Solution:**
1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Verify `NEXT_PUBLIC_API_URL` = `https://shuaibali-todo-backend.hf.space`
3. Redeploy: Deployments → ⋯ → Redeploy

### Issue 3: CORS Errors

**Error:** `Access to fetch at '...' has been blocked by CORS policy`

**Solution:**

Update `backend/src/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-app-name.vercel.app",  # Add your Vercel URL
        "https://*.vercel.app",  # Allow all Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy backend to HuggingFace.

### Issue 4: Database Connection Fails

**Error:** `asyncpg.exceptions.InvalidAuthorizationSpecificationError`

**Solution:**
1. Go to Neon Dashboard: https://console.neon.tech/
2. Verify database is active
3. Check connection string is correct
4. Ensure SSL mode is enabled: `?sslmode=require`
5. Update HuggingFace env var if needed

### Issue 5: 422 Validation Errors

**Cause:** Request body/params don't match backend schema

**Solution:**
1. Check backend logs in HuggingFace Space
2. Verify request format matches API docs: `/docs`
3. Ensure JWT token is valid (not expired)
4. Clear localStorage and re-login

### Issue 6: Environment Variables Not Loading

**Vercel:**
- Only `NEXT_PUBLIC_*` vars are exposed to browser
- Other env vars only available server-side
- After adding env vars, **must redeploy**

**HuggingFace:**
- Env vars set in Space settings
- Must **Factory reboot** after changes

---

## 📊 Deployment Architecture

```
┌─────────────────────────────────────────┐
│           User's Browser                │
└──────────────┬──────────────────────────┘
               │ HTTPS
               ▼
┌─────────────────────────────────────────┐
│          Vercel CDN                     │
│   (Frontend - Next.js)                  │
│   https://your-app.vercel.app           │
│                                         │
│   Environment:                          │
│   - NEXT_PUBLIC_API_URL                 │
└──────────────┬──────────────────────────┘
               │ API Calls (HTTPS)
               │ Authorization: Bearer <JWT>
               ▼
┌─────────────────────────────────────────┐
│      HuggingFace Spaces                 │
│   (Backend - FastAPI + Docker)          │
│   https://shuaibali-todo-backend.hf.space│
│                                         │
│   Environment:                          │
│   - DATABASE_URL                        │
│   - SECRET_KEY                          │
│   - OPENAI_API_KEY                      │
└──────────────┬──────────────────────────┘
               │ PostgreSQL Connection
               │ SSL/TLS
               ▼
┌─────────────────────────────────────────┐
│      Neon PostgreSQL                    │
│   (Serverless Database)                 │
│   ep-steep-union-ai8qcccs.neon.tech    │
│                                         │
│   - Auto-scaling                        │
│   - Branching support                   │
│   - Connection pooling                  │
└─────────────────────────────────────────┘
```

---

## 🎉 Success Criteria

Your deployment is complete when:

✅ **Backend (HuggingFace):**
- `/health` returns 200 OK
- `/docs` shows Swagger UI
- Database connection successful
- API endpoints respond correctly

✅ **Frontend (Vercel):**
- App loads without errors
- Authentication works (login/register)
- Dashboard displays tasks
- CRUD operations work
- No CORS errors
- No 422/405 errors

✅ **Integration:**
- Frontend successfully calls backend APIs
- JWT authentication works
- Data persists in Neon database
- Real-time updates (SSE) functional
- AI chat responds correctly

✅ **Performance:**
- Page load < 3 seconds
- API responses < 500ms
- No memory leaks
- Smooth UI interactions

---

## 📝 Quick Commands Reference

### Vercel CLI Commands

```bash
# Login
vercel login

# Deploy to production
vercel --prod

# Add environment variable
vercel env add VARIABLE_NAME production

# List deployments
vercel list

# View logs
vercel logs [deployment-url]

# Remove deployment
vercel remove [deployment-name]

# Link local project to Vercel
vercel link
```

### Git Deployment Workflow

```bash
# Make changes
git add .
git commit -m "Description of changes"
git push origin master

# Vercel auto-deploys on push (if GitHub integration enabled)
# Check status at: https://vercel.com/dashboard
```

### Update Environment Variables

**Vercel:**
```bash
vercel env add NEXT_PUBLIC_API_URL production
vercel --prod  # Redeploy
```

**HuggingFace:**
1. Go to Space → Settings → Variables
2. Update variables
3. Click "Factory reboot"

---

## 🔐 Security Best Practices

Before going live:

1. **Generate Strong SECRET_KEY:**
   ```bash
   openssl rand -hex 32
   # Use output as SECRET_KEY in HuggingFace
   ```

2. **Update CORS to be Specific:**
   ```python
   allow_origins=[
       "https://your-exact-app.vercel.app",
       # Don't use "*" in production
   ]
   ```

3. **Environment Variables:**
   - Never commit `.env` files
   - Use Vercel/HuggingFace secret managers
   - Rotate keys regularly

4. **Database:**
   - Use connection pooling
   - Enable SSL (`sslmode=require`)
   - Regular backups (Neon does this automatically)

5. **Rate Limiting:**
   - Already configured: 100 requests/minute
   - Monitor in production
   - Adjust if needed

---

## 🆘 Getting Help

**Backend Issues:**
- HuggingFace Logs: Space → Logs tab
- Local testing: `cd backend && uvicorn src.main:app --reload`

**Frontend Issues:**
- Vercel Logs: Dashboard → Deployment → View Function Logs
- Local testing: `cd frontend && npm run dev`

**Database Issues:**
- Neon Console: https://console.neon.tech/
- Connection test: Run `backend/verify_neon_db.py`

**Support Resources:**
- Vercel Docs: https://vercel.com/docs
- HuggingFace Docs: https://huggingface.co/docs/hub/spaces
- Neon Docs: https://neon.tech/docs

---

## 📚 Next Steps After Deployment

1. **Custom Domain (Optional):**
   - Vercel: Settings → Domains → Add Domain
   - Point DNS to Vercel

2. **Monitoring:**
   - Set up Vercel Analytics
   - Monitor HuggingFace usage
   - Check Neon database metrics

3. **Performance:**
   - Enable Vercel Edge Functions if needed
   - Optimize images (use Next.js Image component)
   - Add caching headers

4. **CI/CD:**
   - GitHub Actions for tests
   - Automated deployment on merge
   - Preview deployments for PRs

---

**Your Deployment URLs:**
- **Frontend**: Will be `https://full-stack-todo-app-phase-iii.vercel.app` (or custom)
- **Backend**: `https://shuaibali-todo-backend.hf.space`
- **Database**: Neon (connection pooled)

Good luck with your deployment! 🚀
