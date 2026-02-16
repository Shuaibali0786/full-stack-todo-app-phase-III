# 📋 Deployment Checklist for Full-Stack Todo App

Use this checklist to ensure a smooth deployment process.

## Pre-Deployment

### Repository & Code
- [x] Backend `.env` updated with new Neon database URL
- [x] Frontend `.env.production` configured
- [x] `vercel.json` created in frontend directory
- [x] `.dockerignore` created in backend directory
- [ ] All changes committed to Git
- [ ] Code pushed to GitHub master branch
- [ ] No sensitive data in repository (check `.gitignore`)

### Local Testing
- [ ] Backend starts successfully (`cd backend && uvicorn src.main:app --reload`)
- [ ] Frontend starts successfully (`cd frontend && npm run dev`)
- [ ] Can register and login locally
- [ ] Dashboard loads tasks correctly
- [ ] All CRUD operations work
- [ ] No console errors
- [ ] Frontend build succeeds (`npm run build`)

### Accounts & Services
- [ ] GitHub account with repository access
- [ ] Vercel account created (https://vercel.com)
- [ ] HuggingFace account created (https://huggingface.co)
- [ ] Neon database is active and accessible

---

## Backend Deployment (HuggingFace Spaces)

### Environment Variables
Configure these in HuggingFace Space Settings:

- [ ] `DATABASE_URL` = `postgresql+asyncpg://neondb_owner:npg_Q2CPSxjXH1ue@ep-steep-union-ai8qcccs-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require`
- [ ] `SECRET_KEY` = (generate with `openssl rand -hex 32`)
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` = `30`
- [ ] `REFRESH_TOKEN_EXPIRE_DAYS` = `7`
- [ ] `BETTER_AUTH_SECRET` = (your secret)
- [ ] `OPENAI_API_KEY` = `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`
- [ ] `OPENROUTER_BASE_URL` = `https://openrouter.ai/api/v1`
- [ ] `AGENT_MODEL` = `anthropic/claude-3.5-sonnet`
- [ ] `FALLBACK_MODEL` = `anthropic/claude-3.5-sonnet`
- [ ] `RATE_LIMIT_PER_MINUTE` = `100`

### Deployment Steps
- [ ] Go to https://huggingface.co/spaces
- [ ] Access existing space or create new one
- [ ] Name: `todo-backend-phase-iii` (or use existing)
- [ ] SDK: Docker
- [ ] Connect GitHub repository
- [ ] Set root path to `backend/`
- [ ] Add all environment variables above
- [ ] Trigger build/reboot
- [ ] Wait for deployment to complete

### Backend Testing
- [ ] Health check works: `curl https://YOUR-SPACE.hf.space/health`
- [ ] Returns: `{"status":"healthy","service":"todo-api"}`
- [ ] API docs accessible: `https://YOUR-SPACE.hf.space/docs`
- [ ] Can register via API
- [ ] Can login via API
- [ ] Database connection successful (check logs)

**Backend URL:** `_______________________` (fill in after deployment)

---

## Frontend Deployment (Vercel)

### Pre-Deploy Configuration
- [ ] Update `frontend/.env.production` with correct backend URL
- [ ] Verify `vercel.json` exists in frontend directory
- [ ] Run `npm run build` locally to test
- [ ] Fix any build errors

### Deployment via Dashboard
- [ ] Go to https://vercel.com/new
- [ ] Click "Import Git Repository"
- [ ] Select: `full-stack-todo-app-phase-iii`
- [ ] Configure project:
  - Framework: Next.js ✓
  - Root Directory: `frontend` ← **IMPORTANT**
  - Build Command: `npm run build`
  - Output Directory: `.next`
- [ ] Add environment variable:
  - Name: `NEXT_PUBLIC_API_URL`
  - Value: `https://YOUR-BACKEND.hf.space` (use your actual backend URL)
- [ ] Click "Deploy"
- [ ] Wait for build (2-3 minutes)

### Alternative: Vercel CLI
- [ ] Install CLI: `npm install -g vercel`
- [ ] Navigate: `cd frontend`
- [ ] Login: `vercel login`
- [ ] Deploy: `vercel --prod`
- [ ] Add env: `vercel env add NEXT_PUBLIC_API_URL production`
- [ ] Redeploy: `vercel --prod`

**Frontend URL:** `_______________________` (fill in after deployment)

---

## Post-Deployment Testing

### Frontend Tests
- [ ] App loads at Vercel URL
- [ ] No JavaScript errors in console
- [ ] Homepage displays correctly
- [ ] Can navigate to login page
- [ ] Can navigate to register page

### Authentication Tests
- [ ] Can register new account
- [ ] Email validation works
- [ ] Password requirements enforced
- [ ] Registration redirects to dashboard
- [ ] Can logout
- [ ] Can login with credentials
- [ ] Invalid login shows error
- [ ] JWT token stored in localStorage

### Dashboard Tests
- [ ] Dashboard loads after login
- [ ] Tasks list displays
- [ ] Priorities dropdown populates
- [ ] Tags list shows
- [ ] Statistics cards show correct data
- [ ] Loading states work

### CRUD Operations
- [ ] Can create new task
- [ ] New task appears in list
- [ ] Can edit task title
- [ ] Can edit task description
- [ ] Can change task priority
- [ ] Can add/remove tags
- [ ] Can mark task complete
- [ ] Can delete task
- [ ] Changes persist after refresh

### API Integration
- [ ] API calls succeed (check Network tab)
- [ ] `/api/auth/login` → 200 OK
- [ ] `/api/tasks` → 200 OK
- [ ] `/api/priorities` → 200 OK
- [ ] `/api/tags` → 200 OK
- [ ] No CORS errors
- [ ] No 422 validation errors
- [ ] No 405 method not allowed errors
- [ ] Authorization headers present on requests

### Real-Time Features
- [ ] SSE connection established
- [ ] Real-time updates work (if implemented)
- [ ] Chat feature responds (if OpenRouter key valid)
- [ ] No connection drops

### Performance
- [ ] Initial page load < 3 seconds
- [ ] API responses < 500ms
- [ ] No memory leaks (check DevTools)
- [ ] Smooth UI interactions
- [ ] Images load properly

---

## CORS Configuration

If you encounter CORS errors:

### Update Backend CORS
Edit `backend/src/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://YOUR-APP.vercel.app",  # Production
        "https://*.vercel.app",  # Preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- [ ] Updated CORS allow_origins with Vercel URL
- [ ] Committed changes
- [ ] Pushed to GitHub
- [ ] Redeployed backend (Factory reboot on HuggingFace)
- [ ] Tested after CORS update

---

## Security Hardening

### Before Going Public
- [ ] Generate strong SECRET_KEY (use `openssl rand -hex 32`)
- [ ] Update SECRET_KEY in HuggingFace env vars
- [ ] Generate strong BETTER_AUTH_SECRET
- [ ] Remove `allow_origins=["*"]` from CORS (use specific domains)
- [ ] Verify no `.env` files in Git repository
- [ ] Check no API keys in code
- [ ] Enable rate limiting (already configured)
- [ ] Test with different user accounts
- [ ] Verify SQL injection protection (SQLModel handles this)
- [ ] Test XSS protection
- [ ] Ensure HTTPS everywhere

### Database Security
- [ ] SSL enabled on Neon connection (`sslmode=require`)
- [ ] Connection pooling configured
- [ ] Regular backups enabled (Neon does this automatically)
- [ ] Monitor database size and usage

---

## Monitoring & Maintenance

### Set Up Monitoring
- [ ] Vercel Analytics enabled
- [ ] Monitor Vercel Function logs
- [ ] Check HuggingFace Space metrics
- [ ] Monitor Neon database usage
- [ ] Set up error tracking (optional: Sentry)

### Regular Checks
- [ ] Weekly: Check error logs
- [ ] Weekly: Monitor API response times
- [ ] Monthly: Review database size
- [ ] Monthly: Update dependencies
- [ ] Monthly: Rotate API keys (if needed)

---

## Rollback Plan

If deployment fails:

### Frontend Rollback
- [ ] Vercel: Go to Deployments → Previous deployment → Promote to Production

### Backend Rollback
- [ ] HuggingFace: Revert to previous commit in Space settings
- [ ] Or: Restore previous environment variables

### Database Rollback
- [ ] Neon: Use point-in-time restore (if needed)
- [ ] Neon: Switch to previous database branch (if using branching)

---

## Documentation

- [ ] Update README.md with production URLs
- [ ] Document any deployment issues encountered
- [ ] Update environment variables reference
- [ ] Create user guide (if needed)
- [ ] Document API endpoints (already in `/docs`)

---

## Custom Domain (Optional)

### Vercel Custom Domain
- [ ] Purchase domain (e.g., from Namecheap, GoDaddy)
- [ ] Go to Vercel → Project → Settings → Domains
- [ ] Add custom domain
- [ ] Update DNS records:
  - Type: `A` Record
  - Name: `@`
  - Value: `76.76.21.21` (Vercel IP)
- [ ] Add www subdomain:
  - Type: `CNAME`
  - Name: `www`
  - Value: `cname.vercel-dns.com`
- [ ] Wait for DNS propagation (up to 48 hours)
- [ ] Verify SSL certificate issued

### Update Backend CORS
- [ ] Add custom domain to CORS allow_origins
- [ ] Redeploy backend

---

## Success Metrics

### Deployment Success
- ✅ Backend deployed and accessible
- ✅ Frontend deployed and accessible
- ✅ Database connected and operational
- ✅ All features working in production
- ✅ No console errors
- ✅ Performance meets targets
- ✅ Security measures in place

### User Experience
- ✅ Fast load times
- ✅ Smooth interactions
- ✅ No broken features
- ✅ Mobile responsive
- ✅ Accessible

---

## Troubleshooting Reference

Common issues and solutions:

| Issue | Solution |
|-------|----------|
| Build fails | Check logs, test `npm run build` locally |
| CORS errors | Update backend CORS config, redeploy |
| 404 on API | Verify `NEXT_PUBLIC_API_URL` is correct |
| Database connection fails | Check DATABASE_URL, verify SSL settings |
| 422 errors | Check request schema, verify JWT token |
| Env vars not working | Redeploy after adding env vars |
| Slow performance | Check API response times, optimize queries |

---

## Support Resources

- **Vercel Docs**: https://vercel.com/docs
- **HuggingFace Docs**: https://huggingface.co/docs/hub/spaces
- **Neon Docs**: https://neon.tech/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Next.js Docs**: https://nextjs.org/docs

---

## Final Checklist

- [ ] All tests pass ✓
- [ ] Performance acceptable ✓
- [ ] Security hardened ✓
- [ ] Documentation updated ✓
- [ ] Monitoring set up ✓
- [ ] Rollback plan tested ✓
- [ ] Team notified ✓
- [ ] **DEPLOYMENT COMPLETE** 🎉

---

**Deployment Date:** _______________
**Deployed By:** _______________
**Production URLs:**
- Frontend: _______________
- Backend: _______________
- Database: Neon (ep-steep-union-ai8qcccs)

**Notes:**
_______________________
_______________________
_______________________
