# Test Verification Guide

## Pre-Test Checklist

- [ ] Backend is running on `http://localhost:8000`
- [ ] Frontend is running on `http://localhost:3000`
- [ ] User is logged in
- [ ] Browser console is open (F12)

---

## Test 1: Dashboard Loads Without Errors ✅

### Steps:
1. Navigate to `http://localhost:3000/dashboard`
2. Wait for page to load
3. Check browser console for errors

### Expected Result:
- ✅ Dashboard loads successfully
- ✅ Tasks table is visible
- ✅ No 422 errors in console
- ✅ No repeated error messages

### If This Fails:
- Check backend logs: `GET /api/v1/tasks/` should return 200
- Check network tab for failed requests
- Verify user is authenticated

---

## Test 2: Chatbot Introduction (Help Message) ✅

### Steps:
1. Open chat panel on dashboard
2. Type: `help`
3. Press Enter

### Expected Result:
```
Thanks 🙂
I'm your smart task assistant.
You can tell me what you need to do, and I'll turn it into tasks for you.

You can say things like:
• Add task: I am going to Karachi
• Create task: Project meeting tomorrow
• Show my tasks
• Update task priority to high
• Delete completed task

Just type your task — I'll handle the rest 👍
```

### Validation:
- ✅ Response appears within 1 second (no LLM call)
- ✅ Friendly and helpful message
- ✅ Includes clear examples

---

## Test 3: Create Task in ONE Message ✅

### Steps:
1. In chat, type: `create task I am going to Karachi`
2. Press Enter
3. Wait for response

### Expected Result:
```
✅ Task added!
ID: 8f23a9c1
Title: going to Karachi
Time: 09:03 AM
```

### Validation:
- ✅ Task created immediately (no follow-up questions)
- ✅ Task appears in tasks table
- ✅ Title is correct: "going to Karachi" (not "I am going to Karachi")
- ✅ Response within 2 seconds

---

## Test 4: Show Tasks ✅

### Steps:
1. In chat, type: `show tasks`
2. Press Enter

### Expected Result:
```
Here are your tasks:
1️⃣ (8f23a9c1) going to Karachi – 09:03 AM
2️⃣ (7b12c3d4) buy milk – 08:45 AM
...
```

### Validation:
- ✅ Lists all tasks
- ✅ Shows short IDs (first 8 chars)
- ✅ Includes timestamps
- ✅ Response within 1 second (no LLM call)

---

## Test 5: Update Task ✅

### Steps:
1. Copy a task ID from the list (e.g., `8f23a9c1`)
2. In chat, type: `update task 8f23a9c1 to going to Lahore`
3. Press Enter

### Expected Result:
```
✅ Task updated!
ID: 8f23a9c1
New title: going to Lahore
```

### Validation:
- ✅ Task updated immediately
- ✅ New title appears in tasks table
- ✅ No errors or delays

---

## Test 6: Delete Task ✅

### Steps:
1. In chat, type: `delete task 8f23a9c1`
2. Press Enter

### Expected Result:
```
✅ Deleted: going to Lahore
```

### Validation:
- ✅ Task deleted immediately
- ✅ Task removed from tasks table
- ✅ Confirmation message shows correct title

---

## Test 7: Chatbot Error Handling (LLM Unavailable) ✅

### Steps:
1. Stop backend
2. Rename `OPENAI_API_KEY` in `.env` to `OPENAI_API_KEY_DISABLED`
3. Restart backend
4. In chat, type any message

### Expected Result:
```
Chat service is currently unavailable.
Please configure OPENAI_API_KEY in backend/.env
to enable AI features.
```

### Validation:
- ✅ No crash or 503 error
- ✅ Helpful error message
- ✅ Dashboard still works
- ✅ Can still create/view/edit tasks via UI

### Cleanup:
1. Rename `OPENAI_API_KEY_DISABLED` back to `OPENAI_API_KEY`
2. Restart backend

---

## Test 8: Appreciative Messages ✅

### Steps:
1. In chat, type: `you are good`
2. Press Enter

### Expected Result:
Shows the same friendly introduction as "help" command.

### Validation:
- ✅ Friendly response
- ✅ No task created
- ✅ Instant response (no LLM call)

---

## Test 9: Dashboard API Endpoints ✅

### Manual API Tests:

```bash
# Test 1: Get tasks (no query params)
curl http://localhost:8000/api/v1/tasks/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected: 200 OK, returns tasks

# Test 2: Get tags (no query params)
curl http://localhost:8000/api/v1/tags/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected: 200 OK, returns tags

# Test 3: Get priorities (no query params)
curl http://localhost:8000/api/v1/priorities/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected: 200 OK, returns priorities

# Test 4: Get tasks with trailing slash removed
curl http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer YOUR_TOKEN"

# Expected: 200 OK, returns tasks
```

### Validation:
- ✅ All return 200 OK
- ✅ No 422 validation errors
- ✅ Both `/tasks` and `/tasks/` work

---

## Test 10: Chat Performance ✅

### Steps:
1. In chat, type: `add task test message 1`
2. Wait for response and note the time
3. Repeat with 5 different messages

### Expected Performance:
- CRUD commands (add, show, update, delete): **< 1 second**
- General conversation: **< 3 seconds**
- Help/Introduction: **Instant**

### Validation:
- ✅ Fast response times
- ✅ No delays or timeouts
- ✅ Consistent performance

---

## All Tests Passing Checklist

- [ ] Test 1: Dashboard loads without errors
- [ ] Test 2: Chatbot shows introduction for "help"
- [ ] Test 3: Create task in one message
- [ ] Test 4: Show tasks works
- [ ] Test 5: Update task works
- [ ] Test 6: Delete task works
- [ ] Test 7: Graceful error handling when LLM unavailable
- [ ] Test 8: Appreciative messages handled correctly
- [ ] Test 9: All API endpoints work
- [ ] Test 10: Fast performance

---

## If Any Test Fails

### Check Backend Logs:
```bash
cd backend
# Look for errors in console
# Check for 422, 500, 503 errors
```

### Check Frontend Console:
```bash
# Open browser console (F12)
# Look for API errors
# Check network tab for failed requests
```

### Common Issues:

**422 Errors:**
- Solution: Clear browser cache, restart backend
- Verify code changes in `tasks.py`, `tags.py`, `priorities.py`

**503/500 Errors:**
- Solution: Check `OPENAI_API_KEY` configuration
- Verify error handling in `ai_chat.py` and `agent_service.py`

**Slow Response:**
- Solution: Verify `max_tokens=500` in `agent_service.py`
- Check backend logs for LLM API calls

**Tasks Not Created:**
- Solution: Check intent detection in `agent_service.py`
- Verify `_extract_task_data()` logic

---

## Success Criteria

✅ **All 10 tests pass**
✅ **Dashboard loads without errors**
✅ **Chatbot responds quickly**
✅ **CRUD operations work in one message**
✅ **Graceful error handling**
✅ **No console errors**

---

**Ready for production! 🎉**
