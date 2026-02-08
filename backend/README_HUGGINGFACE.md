# Todo Backend API - HuggingFace Deployment

This is a FastAPI backend for a full-stack Todo application, designed to run on HuggingFace Spaces.

## 🚀 Live Demo

**API Base URL:** https://shuaibali-todo-backend-3.hf.space

**API Documentation:**
- Swagger UI: https://shuaibali-todo-backend-3.hf.space/docs
- ReDoc: https://shuaibali-todo-backend-3.hf.space/redoc

## 📋 Features

- ✅ User authentication with JWT tokens
- ✅ CRUD operations for tasks, priorities, and tags
- ✅ AI-powered chat assistant (OpenRouter integration)
- ✅ Real-time updates via Server-Sent Events
- ✅ PostgreSQL database (Neon)
- ✅ Automatic API documentation
- ✅ CORS enabled for frontend integration

## 🔧 Environment Variables

Set these in your HuggingFace Space settings:

```env
DATABASE_URL=postgresql+asyncpg://user:password@host/dbname
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openrouter-api-key
AGENT_MODEL=anthropic/claude-3.5-sonnet
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
RATE_LIMIT_PER_MINUTE=100
```

## 📦 Tech Stack

- **Framework:** FastAPI 0.104+
- **Database:** PostgreSQL (via Neon)
- **ORM:** SQLModel
- **Authentication:** JWT (python-jose)
- **Password Hashing:** Passlib with bcrypt
- **Async DB Driver:** asyncpg
- **ASGI Server:** Uvicorn

## 🚦 API Endpoints

### Authentication
- `POST /api/v1/login` - Login with email and password
- `POST /api/v1/register` - Register new user
- `POST /api/v1/refresh` - Refresh access token
- `POST /api/v1/logout` - Logout user

### Tasks
- `GET /api/v1/tasks` - List all tasks (with filters)
- `POST /api/v1/tasks` - Create new task
- `GET /api/v1/tasks/{id}` - Get specific task
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `PATCH /api/v1/tasks/{id}/complete` - Toggle completion

### Metadata
- `GET /api/v1/priorities` - List priorities
- `GET /api/v1/tags` - List tags
- `POST /api/v1/priorities` - Create priority
- `POST /api/v1/tags` - Create tag

### User Profile
- `GET /api/v1/me` - Get current user
- `PUT /api/v1/me` - Update user profile

### AI Chat
- `POST /api/v1/chat` - Send message to AI assistant

### Health
- `GET /health` - Health check endpoint

## 🏗️ Project Structure

```
backend/
├── src/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py       # Authentication endpoints
│   │       ├── tasks.py      # Task CRUD endpoints
│   │       ├── priorities.py # Priority endpoints
│   │       ├── tags.py       # Tag endpoints
│   │       ├── users.py      # User endpoints
│   │       └── ai_chat.py    # AI chat endpoint
│   ├── models/               # SQLModel database models
│   ├── services/             # Business logic
│   ├── core/                 # Config, security, database
│   └── main.py               # FastAPI app entry point
├── Dockerfile                # HuggingFace deployment
└── requirements.txt          # Python dependencies
```

## 🔒 Security

- Passwords hashed with bcrypt
- JWT tokens for authentication
- CORS configured for frontend access
- SQL injection prevention via SQLModel
- Rate limiting enabled
- SSL/TLS for database connections

## 📊 Database Schema

The application uses the following tables:
- `users` - User accounts
- `tasks` - Todo tasks
- `priorities` - Priority levels (High, Medium, Low)
- `tags` - User-defined tags
- `task_tags` - Many-to-many relationship
- `conversations` - AI chat conversations
- `messages` - Chat messages

## 🧪 Testing

Test the API using:

```bash
# Health check
curl https://shuaibali-todo-backend-3.hf.space/health

# Login
curl -X POST https://shuaibali-todo-backend-3.hf.space/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'

# Get tasks (with auth token)
curl https://shuaibali-todo-backend-3.hf.space/api/v1/tasks \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

For issues or questions:
- GitHub Issues: [Create an issue](https://github.com/Shuaibali0786/full-stack-todo-app-phase-III/issues)
- Email: support@yourdomain.com

---

**Built with ❤️ using FastAPI and deployed on HuggingFace Spaces**
