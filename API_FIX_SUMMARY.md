# API Endpoint Fix Summary

## Issues Identified

### 1. **405 Method Not Allowed for POST /api/v1/tasks**
**Root Cause:** Backend routes only had `@router.post("/")` (with trailing slash) but not `@router.post("")` (without trailing slash).

**Impact:**
- POST requests to `/api/v1/tasks` (no slash) returned 405
- POST requests to `/api/v1/tasks/` (with slash) worked

### 2. **Same Issue for Priorities and Tags**
- Same routing issue for `/api/v1/priorities` and `/api/v1/tags`

### 3. **422 Unprocessable Entity for GET requests**
- Likely caused by authentication issues or missing auth token
- Less common: invalid query parameters (but all params are optional with defaults)

## Fixes Applied

### Backend Route Fixes

#### 1. **tasks.py** (backend/src/api/v1/tasks.py:163-164)
```python
# BEFORE
@router.post("/", response_model=TaskResponse)
async def create_task(...)

# AFTER (Added line 164)
@router.post("/", response_model=TaskResponse)
@router.post("", response_model=TaskResponse)  # Handle both /tasks and /tasks/
async def create_task(...)
```

#### 2. **priorities.py** (backend/src/api/v1/priorities.py:53-54)
```python
# BEFORE
@router.post("/", response_model=PriorityResponse)
async def create_priority(...)

# AFTER (Added line 54)
@router.post("/", response_model=PriorityResponse)
@router.post("", response_model=PriorityResponse)  # Handle both /priorities and /priorities/
async def create_priority(...)
```

#### 3. **tags.py** (backend/src/api/v1/tags.py:53-54)
```python
# BEFORE
@router.post("/", response_model=TagResponse)
async def create_tag(...)

# AFTER (Added line 54)
@router.post("/", response_model=TagResponse)
@router.post("", response_model=TagResponse)  # Handle both /tags and /tags/
async def create_tag(...)
```

## Frontend API Calls (Already Correct)

The frontend API calls in `frontend/src/utils/api.ts` are correctly structured:

```typescript
export const taskApi = {
  getTasks: (params?: any) =>
    apiClient.get('/api/v1/tasks', { params }),     // ✅ Correct

  createTask: (taskData: any) =>
    apiClient.post('/api/v1/tasks', taskData),      // ✅ Now works with backend fix

  updateTask: (taskId: string, taskData: any) =>
    apiClient.put(`/api/v1/tasks/${taskId}`, taskData),

  deleteTask: (taskId: string) =>
    apiClient.delete(`/api/v1/tasks/${taskId}`),

  toggleTaskComplete: (taskId: string, isCompleted: boolean) =>
    apiClient.patch(`/api/v1/tasks/${taskId}/complete?is_completed=${isCompleted}`),
};

export const priorityApi = {
  getPriorities: () =>
    apiClient.get('/api/v1/priorities'),             // ✅ Correct

  createPriority: (priorityData: any) =>
    apiClient.post('/api/v1/priorities', priorityData), // ✅ Now works
};

export const tagApi = {
  getTags: () =>
    apiClient.get('/api/v1/tags'),                   // ✅ Correct

  createTag: (tagData: any) =>
    apiClient.post('/api/v1/tags', tagData),         // ✅ Now works
};
```

## Verification Steps

### 1. Restart Backend Server
```bash
cd backend
# Activate virtual environment if needed
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Run the server
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Run API Test Script
```bash
cd backend
python test_api_endpoints.py
```

**Note:** Update `TEST_USER` credentials in `test_api_endpoints.py` before running.

### 3. Test Frontend
```bash
cd frontend
npm run dev
```

Visit `http://localhost:3000/dashboard` and:
1. Check browser console for errors
2. Verify tasks, priorities, and tags load
3. Try creating a new task
4. Verify no 405 or 422 errors

## Authentication Checklist

If you still see 422 errors after backend fix, check:

### 1. **Token Storage**
```typescript
// In browser console:
localStorage.getItem('access_token')  // Should return a JWT token
```

### 2. **Token in Request Headers**
Open browser DevTools → Network tab → Check any API request:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### 3. **Login Flow**
Ensure user is properly logged in:
```typescript
// frontend/src/utils/api.ts:80-81
authApi.login('user@example.com', 'password')
  .then(res => {
    localStorage.setItem('access_token', res.data.access_token);
    localStorage.setItem('refresh_token', res.data.refresh_token);
  });
```

## Expected API Responses

### GET /api/v1/tasks
```json
{
  "tasks": [
    {
      "id": "uuid-string",
      "title": "Task title",
      "description": "Task description",
      "is_completed": false,
      "user_id": "uuid-string",
      "due_date": "2025-01-20",
      "reminder_time": null,
      "created_at": "2025-01-20T10:00:00",
      "updated_at": "2025-01-20T10:00:00"
    }
  ],
  "total": 1,
  "offset": 0,
  "limit": 25
}
```

### GET /api/v1/priorities
```json
[
  {
    "id": "uuid-string",
    "name": "High",
    "value": 3,
    "color": "#FF0000",
    "created_at": "2025-01-20T10:00:00",
    "updated_at": "2025-01-20T10:00:00"
  }
]
```

### GET /api/v1/tags
```json
[
  {
    "id": "uuid-string",
    "name": "Work",
    "color": "#0000FF",
    "user_id": "uuid-string",
    "created_at": "2025-01-20T10:00:00",
    "updated_at": "2025-01-20T10:00:00"
  }
]
```

### POST /api/v1/tasks
**Request:**
```json
{
  "title": "New Task",
  "description": "Task description",
  "priority_id": null,
  "due_date": "2025-01-25",
  "reminder_time": "09:00",
  "tag_ids": []
}
```

**Response:**
```json
{
  "id": "new-uuid",
  "title": "New Task",
  "description": "Task description",
  "is_completed": false,
  "user_id": "user-uuid",
  "due_date": "2025-01-25",
  "reminder_time": "2025-01-25T09:00:00",
  "created_at": "2025-01-20T10:00:00",
  "updated_at": "2025-01-20T10:00:00"
}
```

## Common Error Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 401 | Unauthorized | Missing or invalid auth token |
| 404 | Not Found | Invalid endpoint URL or resource ID |
| 405 | Method Not Allowed | **FIXED** - Was missing POST route without trailing slash |
| 422 | Unprocessable Entity | Auth issue, invalid request body, or query params |
| 500 | Internal Server Error | Database connection issue or backend bug |

## Testing Individual Endpoints

### Using curl:

```bash
# 1. Login and get token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpassword"}' \
  | jq -r '.access_token')

# 2. Get priorities
curl -X GET http://localhost:8000/api/v1/priorities \
  -H "Authorization: Bearer $TOKEN"

# 3. Get tags
curl -X GET http://localhost:8000/api/v1/tags \
  -H "Authorization: Bearer $TOKEN"

# 4. Get tasks
curl -X GET http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN"

# 5. Create task (without trailing slash - now works!)
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task",
    "description": "Testing POST endpoint",
    "priority_id": null,
    "due_date": null,
    "reminder_time": null,
    "tag_ids": []
  }'
```

## Next Steps

1. ✅ Backend routes fixed (POST without trailing slash now works)
2. ✅ Frontend API calls are correct
3. ⏳ Restart backend server
4. ⏳ Test with `test_api_endpoints.py`
5. ⏳ Verify dashboard loads tasks correctly
6. ⏳ Test creating new tasks

## Additional Notes

- All query parameters for GET /tasks are **optional** with safe defaults
- The backend handles invalid UUID formats gracefully (logs warning but continues)
- CORS is enabled for all origins (`allow_origins=["*"]`)
- The API uses JWT Bearer token authentication
- Tokens are automatically refreshed when expired (frontend interceptor)
