# Quick Test Guide - All Fixes Applied ✅

## 🚀 Start Testing in 3 Steps

### Step 1: Start Backend
```bash
cd backend
uvicorn src.main:app --reload
```
**Wait for:** `Application startup complete.`

---

### Step 2: Start Frontend (New Terminal)
```bash
npm run dev
```
**Wait for:** `Ready on http://localhost:3000`

---

### Step 3: Open Browser & Test

#### Test 1: Login Page (No Errors)
1. Open: http://localhost:3000/auth/login
2. **Open DevTools Console** (F12)
3. **✅ VERIFY:** No 401 errors
4. **✅ VERIFY:** No 422 errors
5. **✅ VERIFY:** No "Failed to fetch" errors

#### Test 2: Login Flow
1. Enter credentials:
   - Email: (your registered email)
   - Password: (your password)
2. Click "Login"
3. **✅ VERIFY:** Dashboard loads
4. **✅ VERIFY:** No console errors

#### Test 3: Dashboard Data Loading
1. Check console for successful API calls:
   - ✅ `GET /api/v1/me` → 200 OK
   - ✅ `GET /api/v1/priorities` → 200 OK
   - ✅ `GET /api/v1/tags` → 200 OK
   - ✅ `GET /api/v1/tasks` → 200 OK
2. **✅ VERIFY:** Tasks table displays
3. **✅ VERIFY:** Priorities loaded
4. **✅ VERIFY:** Tags loaded

#### Test 4: Create Task (Fix 405 Error)
1. Click "Add Task" button
2. Fill in:
   - Title: "Test Task"
   - Description: "Testing fixes"
3. Click "Save"
4. **✅ VERIFY:** Task appears in list
5. **✅ VERIFY:** Console shows `POST /api/v1/tasks/` → 200 OK
6. **✅ VERIFY:** No 405 errors

#### Test 5: Toggle Task Completion (Fix Query Param)
1. Click checkbox on any task
2. **✅ VERIFY:** Task completion updates
3. **✅ VERIFY:** Console shows `PATCH /api/v1/tasks/{id}/complete?is_completed=true` → 200 OK
4. **✅ VERIFY:** No 405 or 422 errors

---

## 📊 What Was Fixed

| Issue | Before | After |
|-------|--------|-------|
| Auth Error | ❌ 401 on page load | ✅ No errors, proper auth check |
| Priorities/Tags | ❌ 422 validation errors | ✅ Loads after authentication |
| Task Creation | ❌ 405 method error | ✅ Creates successfully |
| Task Toggle | ❌ Sent as body | ✅ Sent as query param |

---

## 🔍 Debug Checklist

If you still see errors:

### Backend Issues
- [ ] Backend is running on http://localhost:8000
- [ ] Check terminal for errors
- [ ] Verify database connection
- [ ] Run: `curl http://localhost:8000/health` (should return: `{"status":"healthy"}`)

### Frontend Issues
- [ ] Frontend is running on http://localhost:3000
- [ ] Clear browser cache (Ctrl+Shift+Delete)
- [ ] Clear localStorage (DevTools → Application → Local Storage → Clear)
- [ ] Restart frontend dev server

### Network Issues
- [ ] Check DevTools Network tab
- [ ] Look for failed requests
- [ ] Verify request URLs match backend routes
- [ ] Check request headers include Authorization token

---

## 🎯 Success Criteria

### ✅ All Tests Pass When:
1. Login page loads with **zero console errors**
2. Login succeeds and redirects to dashboard
3. Dashboard loads **all data** (tasks, priorities, tags)
4. Can **create new tasks** without errors
5. Can **toggle task completion** without errors
6. All API calls return **200 OK** status

---

## 🆘 Need Help?

### Common Issues

**Issue:** Still seeing 401 errors
- **Solution:** Clear localStorage and refresh page

**Issue:** Tasks not loading
- **Solution:** Check you're logged in with valid credentials

**Issue:** Can't create tasks
- **Solution:** Verify backend is running and database is accessible

**Issue:** Frontend won't start
- **Solution:** Run `npm install` first

---

**Ready to test?** Start with Step 1 above! 🚀
