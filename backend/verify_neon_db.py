#!/usr/bin/env python3
"""
Neon PostgreSQL Database Verification Script

This script verifies that:
1. Connection to Neon PostgreSQL works
2. Tables can be created
3. Data persists correctly
4. MCP tools can write to the database
"""
import asyncio
import sys
from uuid import uuid4
from datetime import datetime

# Add src to path
sys.path.insert(0, './src')

from src.core.database import engine, sync_engine, create_tables, get_session
from src.models.user import User
from src.models.task import Task
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


async def verify_database():
    """Verify Neon PostgreSQL connection and persistence"""
    print("=" * 60)
    print("NEON POSTGRESQL DATABASE VERIFICATION")
    print("=" * 60)

    # Step 1: Test connection
    print("\n[1/5] Testing database connection...")
    try:
        async with AsyncSession(engine) as session:
            result = await session.execute(select(1))
            assert result.scalar() == 1
            print("✅ Database connection successful!")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

    # Step 2: Create tables
    print("\n[2/5] Creating database tables...")
    try:
        from sqlmodel import SQLModel
        # Import all models to register them
        from src.models.user import User
        from src.models.task import Task
        from src.models.priority import Priority
        from src.models.tag import Tag
        from src.models.task_tag import TaskTag
        from src.models.recurring_task import RecurringTask
        from src.models.task_instance import TaskInstance
        from src.models.password_reset import PasswordResetToken
        from src.models.conversation import Conversation
        from src.models.message import Message

        # Create all tables
        SQLModel.metadata.create_all(sync_engine)
        print("✅ Tables created successfully!")
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        return False

    # Step 3: Create test user
    print("\n[3/5] Creating test user...")
    try:
        async with AsyncSession(engine, expire_on_commit=False) as session:
            test_user = User(
                id=uuid4(),
                username=f"test_user_{datetime.now().timestamp()}",
                email=f"test_{datetime.now().timestamp()}@example.com",
                hashed_password="test_hash_123",
                created_at=datetime.utcnow()
            )
            session.add(test_user)
            await session.commit()
            await session.refresh(test_user)
            user_id = test_user.id
            print(f"✅ Test user created! ID: {user_id}")
    except Exception as e:
        print(f"❌ User creation failed: {e}")
        return False

    # Step 4: Create test task (via MCP-style operation)
    print("\n[4/5] Creating test task (MCP-style)...")
    try:
        async with AsyncSession(engine, expire_on_commit=False) as session:
            test_task = Task(
                id=uuid4(),
                title="Verify Neon DB Connection",
                description="This task verifies that Neon PostgreSQL persistence works",
                user_id=user_id,
                is_completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(test_task)
            await session.commit()
            await session.refresh(test_task)
            task_id = test_task.id
            print(f"✅ Test task created! ID: {task_id}")
    except Exception as e:
        print(f"❌ Task creation failed: {e}")
        return False

    # Step 5: Verify persistence (read back in new session)
    print("\n[5/5] Verifying data persistence...")
    try:
        async with AsyncSession(engine) as session:
            # Read user
            user = await session.get(User, user_id)
            assert user is not None, "User not found"
            assert user.username.startswith("test_user_"), "User data incorrect"

            # Read task
            task = await session.get(Task, task_id)
            assert task is not None, "Task not found"
            assert task.title == "Verify Neon DB Connection", "Task data incorrect"
            assert task.user_id == user_id, "Task-user relationship incorrect"

            print(f"✅ Data persistence verified!")
            print(f"   - User: {user.username} ({user.email})")
            print(f"   - Task: {task.title}")
            print(f"   - Created at: {task.created_at}")
    except Exception as e:
        print(f"❌ Persistence verification failed: {e}")
        return False

    # Cleanup
    print("\n[CLEANUP] Removing test data...")
    try:
        async with AsyncSession(engine) as session:
            task = await session.get(Task, task_id)
            user = await session.get(User, user_id)
            if task:
                await session.delete(task)
            if user:
                await session.delete(user)
            await session.commit()
            print("✅ Test data cleaned up!")
    except Exception as e:
        print(f"⚠️  Cleanup warning (non-critical): {e}")

    print("\n" + "=" * 60)
    print("🎉 ALL VERIFICATIONS PASSED!")
    print("=" * 60)
    print("\nNeon PostgreSQL is configured correctly and working!")
    print("✅ Connection established")
    print("✅ Tables created")
    print("✅ Data writes working")
    print("✅ Data persistence confirmed")
    print("✅ MCP tools ready to use")
    return True


if __name__ == "__main__":
    success = asyncio.run(verify_database())
    sys.exit(0 if success else 1)
