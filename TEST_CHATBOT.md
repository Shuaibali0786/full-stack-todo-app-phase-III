# Chatbot Testing Guide

## Quick Test Scenarios

### 1. Test Greeting (Fixed)
**Input:** `hi`
**Expected Output:**
```
I'm TaskFlow AI 🙂
I help you manage your tasks quickly.

You can use any natural sentence, for example:
• Add task: I am going to Karachi
• Create task: Project meeting tomorrow
• Show my tasks
• Update task priority to high
• Delete task [name or ID]
• Complete task [name or ID]

Just type naturally — I'll understand and act instantly!
```

---

### 2. Test Instant Create
**Input:** `I am going to Karachi tomorrow`
**Expected:**
```
✅ Task added!
ID: 8f23a9c1
Title: going to Karachi tomorrow
Time: 09:03 AM
```

**Verify:** Check dashboard - task should appear instantly!

---

### 3. Test Show Tasks
**Input:** `show my tasks`
**Expected:**
```
Here are your tasks:
1️⃣ (8f23a9c1) going to Karachi tomorrow – 09:03 AM
2️⃣ (a1b2c3d4) buy groceries – 08:45 AM
```

---

### 4. Test Complete (NEW - Was Broken)
**Input:** `complete task 8f23a9c1`
**Expected:**
```
✅ Completed: going to Karachi tomorrow
```

**Or try by name:**
**Input:** `complete task going to Karachi`
**Expected:**
```
✅ Completed: going to Karachi tomorrow
```

**Verify:** Check dashboard - task should be marked complete!

---

### 5. Test Update
**Input:** `update task 8f23a9c1 to buy milk and bread`
**Expected:**
```
✅ Task updated!
ID: 8f23a9c1
New title: buy milk and bread
```

**Verify:** Check dashboard - task title should update instantly!

---

### 6. Test Delete
**Input:** `delete task 8f23a9c1`
**Expected:**
```
✅ Deleted: buy milk and bread
```

**Verify:** Check dashboard - task should disappear instantly!

---

### 7. Test Error Handling (Fixed)
**Input:** `asdfghjkl`
**Expected (NOT "Unable to process"):**
```
I'm not sure what you want to do. Try these commands:

📝 **Create tasks:**
• "add task buy groceries"
• "meeting tomorrow at 3pm"

📋 **View tasks:**
• "show tasks"
• "list my tasks"

✏️ **Update tasks:**
• "update task [ID] to [new title]"

✅ **Complete tasks:**
• "complete task [ID or name]"

❌ **Delete tasks:**
• "delete task [ID or name]"

Type 'help' for more info!
```

---

### 8. Test Natural Language Create
**Input:** `meeting with John tomorrow at 3pm`
**Expected:**
```
✅ Task added!
ID: xyz123
Title: meeting with John
Time: XX:XX AM
```

---

### 9. Test Multiple Natural Variations

#### Complete variations:
- `mark task done 8f23a9c1`
- `complete task going to Karachi`
- `finish task buy milk`
- `mark as complete 8f23a9c1`

All should work instantly!

#### Update variations:
- `change task 8f23a9c1 to new title`
- `update buy milk to buy almond milk`
- `edit task 8f23a9c1 to new title`

#### Delete variations:
- `remove task 8f23a9c1`
- `delete going to Karachi`
- `cancel task buy milk`

---

## Dashboard Sync Test

### Step-by-Step:

1. **Open dashboard** in browser
2. **Open chatbot** in same browser
3. **Create task via chatbot:** "buy groceries tomorrow"
4. **Check dashboard** → Should appear immediately
5. **Update task via chatbot:** "update task [ID] to buy milk"
6. **Check dashboard** → Should update immediately
7. **Complete task via chatbot:** "complete task [ID]"
8. **Check dashboard** → Should mark as complete immediately
9. **Delete task via chatbot:** "delete task [ID]"
10. **Check dashboard** → Should disappear immediately

**All changes should sync in real-time** (within 1-2 seconds max)

---

## Console Logs to Watch

When testing, monitor backend console for:

```
[AGENT SERVICE] Processing message for user_id: xxx
[AGENT SERVICE] Message: buy groceries
[AGENT SERVICE] Got conversation with ID: xxx
[AGENT SERVICE] Stored user message
[AGENT SERVICE] Retrieved X context messages
[AGENT SERVICE] Processing with agent...
[AGENT SERVICE] Agent response: ✅ Task added!...
[AGENT SERVICE] Stored agent response
```

**No errors should appear!**

---

## What Changed (Summary)

### ✅ Fixed Issues:

1. **COMPLETE intent** - Now works instantly (was asking questions before)
2. **Greeting message** - Updated to match exact requirements
3. **Error handling** - No more generic "Unable to process" errors
4. **System prompt** - More action-focused
5. **Unknown intents** - Helpful guidance instead of API calls

### ✅ Already Working:

1. **Dashboard sync** - Via shared DB session + SSE
2. **CREATE intent** - Instant task creation
3. **READ intent** - Instant task listing
4. **UPDATE intent** - Instant task updates
5. **DELETE intent** - Instant task deletion

---

## Expected Performance

- **Response time:** < 500ms for all commands
- **Dashboard sync:** 1-2 seconds max
- **No API failures:** Unknown intents don't call OpenRouter
- **Clear feedback:** Every action gets confirmation

---

## Troubleshooting

### If chatbot doesn't respond:
1. Check if backend is running: `http://localhost:8000/docs`
2. Check console logs for errors
3. Verify OPENAI_API_KEY in `.env` (if using AI features)

### If tasks don't appear on dashboard:
1. Refresh the dashboard page
2. Check if SSE is connected (check Network tab)
3. Verify user is logged in with same account

### If "Unable to process" appears:
This should NOT happen anymore! If it does:
1. Check backend console logs
2. Report the exact message that triggered it
3. Check if database is accessible

---

## Next Steps After Testing

1. ✅ Verify all test scenarios pass
2. ✅ Confirm dashboard sync works
3. ✅ Check no console errors
4. 🎉 **Deploy to production!**
