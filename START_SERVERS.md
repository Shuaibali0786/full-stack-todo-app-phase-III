# 🚀 Quick Start Guide - TaskFlow AI

## Step-by-Step Instructions

### 1️⃣ Start Backend (Terminal 1)

```bash
# Navigate to backend
cd backend

# Activate virtual environment (Windows)
venv\Scripts\activate

# If you see any errors about missing packages:
pip install -r requirements.txt

# Start the server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**✅ Success looks like:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
[AGENT SERVICE] Initialized with model: openai/gpt-4-turbo
INFO:     Application startup complete.
```

**❌ If you see errors:**

#### Error: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

#### Error: "OPENAI_API_KEY not configured"
- Your OpenRouter API key is already set correctly in `.env`
- This error shouldn't happen

#### Error: "Port 8000 is already in use"
```bash
# Kill the existing process
taskkill /F /IM python.exe
# Then restart
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

---

### 2️⃣ Start Frontend (Terminal 2 - NEW WINDOW)

```bash
# Navigate to frontend
cd frontend

# If first time or after pulling changes:
npm install

# Start the dev server
npm run dev
```

**✅ Success looks like:**
```
▲ Next.js 14.x.x
- Local:        http://localhost:3000
✓ Ready in 2.5s
```

**❌ If you see errors:**

#### Error: "Port 3000 is already in use"
```bash
# Windows: Kill the process
taskkill /F /IM node.exe
# Then restart
npm run dev
```

---

### 3️⃣ Open App

1. Open browser: **http://localhost:3000**
2. Login with your credentials
3. You should see the dashboard with the AI chatbot!

---

## 🔍 Troubleshooting CORS Errors

If you see CORS errors in the browser console:

### Check 1: Is Backend Running?
```bash
# In a new terminal, test:
curl http://localhost:8000/health
```

**Should return:**
```json
{"status":"healthy","service":"todo-api"}
```

**If it fails:**
- Backend is not running
- Go back to Step 1 and restart backend

### Check 2: Backend Logs
Look at the backend terminal for errors. Common issues:
- Import errors
- Database errors
- Missing dependencies

### Check 3: Restart Both Servers
1. Stop both servers (Ctrl+C in each terminal)
2. Start backend first (wait for "Application startup complete")
3. Start frontend second
4. Refresh browser

---

## 🧪 Test the Chatbot

Once everything is running:

1. **Type a message:** "Hello"
2. **AI should respond:** A friendly greeting
3. **Try:** "Show all my tasks"
4. **AI should list:** Your tasks or say you have none
5. **Try:** "Add task buy milk tomorrow"
6. **AI should create:** A new task

---

## 📝 Quick Reference

| Issue | Solution |
|-------|----------|
| CORS errors | Restart backend server |
| 401 Unauthorized | Check if you're logged in |
| Chatbot not responding | Check backend logs for errors |
| Port in use | Kill process and restart |
| Module not found | `pip install -r requirements.txt` |
| npm errors | `rm -rf node_modules && npm install` |

---

## ⚠️ Important Notes

1. **Always start backend FIRST**, then frontend
2. **Wait for backend** to show "Application startup complete" before starting frontend
3. **OpenRouter API key** is already configured in `.env`
4. **Both servers must be running** for the app to work
5. **Check backend terminal** for error messages if chatbot fails

---

## 🆘 Still Having Issues?

### Get Backend Logs
```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
```

### Check If Ports Are Free
```bash
# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :3000
```

### Test OpenRouter Connection
```bash
cd backend
python test_openrouter.py
```

Should show: `✅ SUCCESS! Response from OpenRouter`
