# 🚀 TaskFlow AI - Quick Start Guide

## 🚨 CRITICAL: Backend Must Be Running!

**ALL your errors are caused by the backend not running:**
- ❌ Registration/login timeouts
- ❌ 401/422 API errors
- ❌ Dashboard not loading
- ❌ Chatbot not working

**Solution: Start the backend first!**

---

## ✅ Quick Start (2 Steps)

### Step 1: Start Backend (Terminal 1)

**Option A - Using startup script (Recommended):**
```bash
.\START_BACKEND.bat
```

**Option B - Manual:**
```bash
cd backend
python -m uvicorn src.main:app --reload
```

**Wait for:**
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 2: Start Frontend (Terminal 2)

**Option A - Using startup script (Recommended):**
```bash
.\START_FRONTEND.bat
```

**Option B - Manual:**
```bash
npm run dev
```

**Wait for:**
```
VITE ready in XXXms
Local: http://localhost:3000
```

---

## 🧪 Verify Everything Works

### 1. Test Backend Health
Open browser: http://localhost:8000/health

**Expected:**
```json
{"status":"healthy","service":"todo-api"}
```

### 2. Test API Documentation
Open browser: http://localhost:8000/docs

**Expected:** Interactive Swagger UI showing all endpoints

### 3. Test Frontend
Open browser: http://localhost:3000

**Expected:** TaskFlow AI login page loads

---

## 🎯 Complete User Flow Test

Once both servers are running:

1. **Register New User**
   - Go to: http://localhost:3000/auth/register
   - Fill in: Email, Password, First Name, Last Name
   - Click "Register"
   - **Expected:** Redirect to login page with success message

2. **Login**
   - Email: (your registered email)
   - Password: (your password)
   - Click "Login"
   - **Expected:** Redirect to dashboard

3. **Dashboard Loads**
   - **Expected:**
     - ✅ No console errors
     - ✅ Task table displays
     - ✅ "Add Task" button visible
     - ✅ Chatbot sidebar visible

4. **Add Task (Button)**
   - Click "Add Task" button
   - Fill in task details
   - Click "Save"
   - **Expected:** Task appears in table immediately

5. **Add Task (Chatbot)**
   - In chatbot: "Add task: Meeting tomorrow"
   - **Expected:**
     - ✅ Chatbot responds with confirmation
     - ✅ Task appears in dashboard table
     - ✅ No page refresh needed

6. **Toggle Task Completion**
   - Click checkbox on any task
   - **Expected:**
     - ✅ Task marked complete
     - ✅ Visual feedback (strikethrough)

---

## 🔧 Troubleshooting

### Backend Won't Start

**Error: "Address already in use"**
```bash
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Error: "Module not found"**
```bash
cd backend
pip install -r requirements.txt
```

**Error: "Database connection failed"**
- Check `.env` file has correct DATABASE_URL
- Verify Neon PostgreSQL database is accessible
- Test connection: `python backend/verify_neon_db.py`

### Frontend Won't Start

**Error: "Port 3000 already in use"**
```bash
# Kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

**Error: "npm: command not found"**
- Install Node.js: https://nodejs.org/
- Verify: `node --version`

**Error: "Module not found"**
```bash
npm install
```

### API Errors After Starting

**422 Errors on API calls:**
- ✅ **FIXED** - Import order in `deps.py`
- Restart backend to apply fix

**401 Unauthorized:**
- Normal for unauthenticated requests
- Login first to get JWT token

**Timeouts:**
- Backend not running or slow database
- Check backend terminal for errors
- Verify DATABASE_URL in `.env`

### Chatbot Slow/Not Working

**"Unable to process your request":**
- Check `OPENAI_API_KEY` in `backend/.env`
- Verify API key is valid: https://platform.openai.com/api-keys
- Check backend logs for OpenAI API errors

**Slow responses:**
- Normal for GPT-4 (can take 5-10 seconds)
- Check network connectivity
- Monitor backend logs for API latency

---

## 📊 What's Fixed

| Issue | Status | Fix Applied |
|-------|--------|-------------|
| Import error (422s) | ✅ Fixed | Moved `select` import to top |
| Trailing slash redirects | ✅ Fixed | Removed from API calls |
| Auth flow timing | ✅ Fixed | Better state management |
| Task toggle | ✅ Fixed | Query param instead of body |
| Backend startup | ✅ Documented | Created START_BACKEND.bat |
| Frontend startup | ✅ Documented | Created START_FRONTEND.bat |

---

## 📁 Useful Files

- **START_BACKEND.bat** - One-click backend startup
- **START_FRONTEND.bat** - One-click frontend startup
- **TEST_RESULTS.md** - Backend API test results
- **FIX_SUMMARY_422_ERRORS.md** - Technical fix documentation
- **CRITICAL_FIX_APPLIED.md** - Import error deep dive

---

## 🆘 Still Not Working?

1. **Check both terminals for errors**
   - Backend terminal: Python/database errors
   - Frontend terminal: Node/build errors

2. **Clear all caches**
   ```bash
   # Browser
   F12 → Right-click Refresh → Empty Cache and Hard Reload

   # Node modules
   rm -rf node_modules
   npm install
   ```

3. **Verify environment**
   - Backend `.env` has DATABASE_URL and OPENAI_API_KEY
   - Database is accessible
   - No firewall blocking ports 3000 or 8000

4. **Check logs**
   - Backend: Look for startup errors or API failures
   - Frontend: Check browser console (F12)
   - Network: Check DevTools Network tab for failed requests

---

## 🎉 Success Indicators

When everything works:

✅ Backend: `Application startup complete`
✅ Frontend: `VITE ready`
✅ Health: http://localhost:8000/health returns 200
✅ Docs: http://localhost:8000/docs loads Swagger UI
✅ Login: User can register and login
✅ Dashboard: Loads without errors, shows task table
✅ API: All endpoints return 200/201 (when authenticated)
✅ Chatbot: Responds quickly and adds tasks correctly
✅ Tasks: Can create, complete, update, delete

---

**Next Steps:**
1. ✅ Run `.\START_BACKEND.bat` in Terminal 1
2. ✅ Run `.\START_FRONTEND.bat` in Terminal 2
3. ✅ Open http://localhost:3000 in browser
4. ✅ Register → Login → Test dashboard
5. ✅ Try chatbot: "Add task: Test the chatbot"

**Status:** 🚀 **READY TO START!**
