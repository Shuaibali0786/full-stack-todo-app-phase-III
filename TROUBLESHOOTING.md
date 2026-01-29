# 🔧 Troubleshooting Guide - CORS & 401 Errors

## 🚨 You're Seeing These Errors:

```
Failed to load resource: the server responded with a status of 401 (Unauthorized)
Access to XMLHttpRequest at 'http://localhost:8000/api/v1/tasks/' blocked by CORS policy
```

---

## ✅ IMMEDIATE FIX

### Step 1: Check if Backend is Running

Open a new terminal and run:
```bash
curl http://localhost:8000/health
```

**If you get an error or "connection refused":**
➡️ **Backend is NOT running!** Go to Step 2.

**If you get `{"status":"healthy","service":"todo-api"}`:**
➡️ Backend is running. Go to Step 3.

---

### Step 2: Start the Backend (If Not Running)

#### Option A: Use the Batch File (Easiest)
```bash
# Navigate to backend folder
cd backend

# Double-click this file or run:
start_backend.bat
```

#### Option B: Manual Start
```bash
cd backend
venv\Scripts\activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Wait for this message:**
```
INFO:     Application startup complete.
```

**If you see errors**, check the "Common Backend Errors" section below.

---

### Step 3: Clear Browser Cache & Reload

1. Open DevTools (F12)
2. Right-click the refresh button
3. Select **"Empty Cache and Hard Reload"**
4. Or: Close browser completely and reopen

---

### Step 4: Check Authentication

The 401 error means you're not authenticated. Try:

1. **Logout and Login Again:**
   - Click the Logout button
   - Login with your credentials
   - The `access_token` will be refreshed

2. **Check localStorage:**
   - Open DevTools (F12)
   - Go to Application → Local Storage → http://localhost:3000
   - Look for `access_token`
   - If missing or expired, logout and login again

---

## 🐛 Common Backend Errors

### Error: "ModuleNotFoundError: No module named 'openai'"

**Fix:**
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

### Error: "Table 'conversations' not found"

**Fix:** Restart the backend. Tables are created on startup.
```bash
# Stop backend (Ctrl+C)
# Start again
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Error: "Address already in use (port 8000)"

**Fix:**
```bash
# Windows: Kill existing process
taskkill /F /IM python.exe

# Then restart
cd backend
venv\Scripts\activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Error: "OPENAI_API_KEY not configured"

**Check:** Your `.env` file should have:
```env
OPENAI_API_KEY=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
```

If it's commented out (has `#` at the start), remove the `#`.

---

## 🔍 Debug Checklist

Run through this checklist:

- [ ] Backend is running on port 8000
  ```bash
  curl http://localhost:8000/health
  ```

- [ ] Frontend is running on port 3000
  ```bash
  curl http://localhost:3000
  ```

- [ ] You're logged in (check DevTools → Application → localStorage → `access_token`)

- [ ] Both terminals show no errors

- [ ] Backend logs show:
  ```
  INFO:     Application startup complete.
  [AGENT SERVICE] Initialized with model: openai/gpt-4-turbo
  ```

- [ ] Browser console is clear of CORS errors

---

## 🔄 Nuclear Option: Full Restart

If nothing works, do a complete restart:

### 1. Stop Everything
- Close both terminals (Ctrl+C)
- Close browser
- Kill all Python and Node processes:
  ```bash
  taskkill /F /IM python.exe
  taskkill /F /IM node.exe
  ```

### 2. Start Backend Fresh
```bash
cd E:\full-stack-todo-app-phaze-III\backend
venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Wait for:** `INFO: Application startup complete.`

### 3. Start Frontend Fresh
```bash
# In a NEW terminal
cd E:\full-stack-todo-app-phaze-III\frontend
npm run dev
```

**Wait for:** `✓ Ready in X.Xs`

### 4. Open Browser Fresh
1. Open a new browser window
2. Go to: http://localhost:3000
3. Login
4. Test the chatbot

---

## 📝 What's Happening?

### CORS Error Explained
- **What it means:** Frontend (port 3000) can't talk to Backend (port 8000)
- **Why it happens:** Backend is not running OR CORS is not configured
- **How we fixed it:** Backend has `allow_origins=["*"]` in `main.py`

### 401 Unauthorized Explained
- **What it means:** You're not logged in or token expired
- **Why it happens:** Token missing or invalid in localStorage
- **How to fix it:** Logout and login again

---

## 🆘 Still Broken?

### Get Detailed Backend Logs
```bash
cd backend
venv\Scripts\activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
```

Copy the error message and look for:
- Python tracebacks
- Import errors
- Database errors
- Configuration errors

### Test OpenRouter Integration
```bash
cd backend
python test_openrouter.py
```

Should show: `✅ SUCCESS! Response from OpenRouter`

If this fails, your OpenRouter API key might be invalid.

---

## ✅ Success Criteria

You'll know everything is working when:

1. **Backend Terminal Shows:**
   ```
   INFO:     Application startup complete.
   [AGENT SERVICE] Initialized with model: openai/gpt-4-turbo
   ```

2. **Frontend Terminal Shows:**
   ```
   ✓ Ready in X.Xs
   ```

3. **Browser Console Shows:**
   - No CORS errors
   - No 401 errors
   - Successful API calls (200 status)

4. **Dashboard Loads:**
   - Tasks table visible
   - Chatbot visible in sidebar
   - Can type in chat and get responses

---

## 🎯 Quick Test

Once everything is running, test with:

```bash
# Test backend health
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000

# Should both return successfully
```

Then in the chatbot, type: **"Hello"**

If AI responds with a friendly greeting, **everything is working!** 🎉
