# Quick Start Guide - Todo App

## What Was Fixed

### ✅ Backend API Routes (405 Error Fixed)
- Added `@router.post("")` (without trailing slash) to:
  - `/api/v1/tasks`
  - `/api/v1/priorities`
  - `/api/v1/tags`

**Before:** POST requests to `/api/v1/tasks` returned 405 Method Not Allowed
**After:** POST requests now work correctly

### ✅ Frontend API Calls
- Already correctly configured in `frontend/src/utils/api.ts`
- Uses proper authentication with JWT tokens
- Automatic token refresh on 401 errors

## Start the Application

### 1. Start Backend (Terminal 1)

```bash
cd backend

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Start server
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend running at: http://localhost:8000
📖 API docs at: http://localhost:8000/docs

### 2. Start Frontend (Terminal 2)

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

✅ Frontend running at: http://localhost:3000

### 3. Access Application

1. Open browser: http://localhost:3000
2. **Login** with your credentials
3. Navigate to **Dashboard**: http://localhost:3000/dashboard
4. Tasks, priorities, and tags should now load correctly!

## Verify Everything Works

### Test Backend API (Optional)

```bash
cd backend
python test_api_endpoints.py
```

**Note:** Update `TEST_USER` credentials in the script first.

### Check Frontend Console

1. Open browser DevTools (F12)
2. Go to **Console** tab
3. Should see **no 405 or 422 errors**
4. Network tab should show:
   - ✅ GET /api/v1/priorities → 200 OK
   - ✅ GET /api/v1/tags → 200 OK
   - ✅ GET /api/v1/tasks → 200 OK
   - ✅ POST /api/v1/tasks → 200 OK (when creating task)

## Troubleshooting

### Still Getting 422 Errors?

#### Check Authentication Token:
```javascript
// In browser console:
localStorage.getItem('access_token')
```

**If null or undefined:**
1. Logout and login again
2. Token should be stored after successful login

#### Check Network Request Headers:
1. Open DevTools → Network tab
2. Click any API request (e.g., GET /api/v1/tasks)
3. Check **Request Headers**:
   ```
   Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
   ```

**If missing:**
- Login again to get fresh token
- Check if localStorage is enabled in browser

### Backend Not Starting?

#### Check Database Connection:
```bash
cd backend
python verify_neon_db.py
```

#### Check Environment Variables:
Create `backend/.env` if missing:
```env
DATABASE_URL=postgresql://user:password@host/dbname
SECRET_KEY=your-secret-key-here
OPENROUTER_API_KEY=your-openrouter-key  # Optional
```

### Frontend API URL Wrong?

Create `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Note:** Use `.env.local.example` as a template.

## API Endpoints Overview

### Authentication
- POST `/api/v1/login` - Login and get JWT token
- POST `/api/v1/register` - Create new account
- POST `/api/v1/refresh` - Refresh expired token

### Tasks
- GET `/api/v1/tasks` - List all tasks (with filters)
- POST `/api/v1/tasks` - Create new task ✅ **FIXED**
- GET `/api/v1/tasks/{id}` - Get specific task
- PUT `/api/v1/tasks/{id}` - Update task
- DELETE `/api/v1/tasks/{id}` - Delete task
- PATCH `/api/v1/tasks/{id}/complete` - Toggle completion

### Metadata
- GET `/api/v1/priorities` - List all priority levels
- GET `/api/v1/tags` - List user's tags
- POST `/api/v1/priorities` - Create priority ✅ **FIXED**
- POST `/api/v1/tags` - Create tag ✅ **FIXED**

### User
- GET `/api/v1/me` - Get current user profile
- PUT `/api/v1/me` - Update user profile

## Sample API Calls

### Create Task (JavaScript/TypeScript)

```typescript
import { taskApi } from '@/utils/api';

const newTask = {
  title: "Complete project",
  description: "Finish the todo app",
  priority_id: null,  // Optional: UUID of priority
  due_date: "2025-01-25",  // Optional: YYYY-MM-DD
  reminder_time: "09:00",  // Optional: HH:MM
  tag_ids: []  // Optional: Array of tag UUIDs
};

try {
  const response = await taskApi.createTask(newTask);
  console.log('Task created:', response.data);
} catch (error) {
  console.error('Error creating task:', error);
}
```

### Get Tasks with Filters

```typescript
import { taskApi } from '@/utils/api';

// Get incomplete tasks, sorted by due date
const params = {
  completed: false,
  sort: 'due_date',
  order: 'asc',
  limit: 50,
  offset: 0
};

try {
  const response = await taskApi.getTasks(params);
  console.log('Tasks:', response.data.tasks);
  console.log('Total:', response.data.total);
} catch (error) {
  console.error('Error fetching tasks:', error);
}
```

### Get Priorities and Tags

```typescript
import { priorityApi, tagApi } from '@/utils/api';

// Load metadata for task form
async function loadMetadata() {
  try {
    const [priorities, tags] = await Promise.all([
      priorityApi.getPriorities(),
      tagApi.getTags()
    ]);

    console.log('Priorities:', priorities.data);
    console.log('Tags:', tags.data);
  } catch (error) {
    console.error('Error loading metadata:', error);
  }
}
```

## Success Checklist

- ✅ Backend starts without errors
- ✅ Frontend starts without errors
- ✅ Can login successfully
- ✅ Dashboard loads without 405/422 errors
- ✅ Tasks display in the table
- ✅ Can create new tasks
- ✅ Priorities and tags load in dropdowns
- ✅ No console errors in browser

## Need Help?

1. Check `API_FIX_SUMMARY.md` for detailed technical explanation
2. Run `backend/test_api_endpoints.py` to verify backend
3. Check browser console and network tab for errors
4. Verify authentication token is present in localStorage
5. Ensure both backend and frontend are running

---

**All Done!** 🎉 Your todo app should now work correctly!
