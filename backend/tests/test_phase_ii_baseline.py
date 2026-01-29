"""
Phase II Baseline Tests

These tests verify that existing Phase II functionality remains intact
after Phase III changes (Constitution Principle VI: Phase-II Protection)
"""
import pytest
from src.models import User, Task, Priority, Tag
from src.core.database import create_tables, sync_engine


def test_phase_ii_models_importable():
    """Verify all Phase II models can be imported"""
    assert User is not None
    assert Task is not None
    assert Priority is not None
    assert Tag is not None


def test_phase_ii_tables_exist():
    """Verify all Phase II tables exist in database"""
    import sqlite3
    conn = sqlite3.connect('todo_app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [t[0] for t in cursor.fetchall()]
    conn.close()

    # Phase II tables
    assert 'users' in tables
    assert 'tasks' in tables
    assert 'priorities' in tables
    assert 'tags' in tables
    assert 'task_tags' in tables
    assert 'recurring_tasks' in tables
    assert 'task_instances' in tables
    assert 'password_reset_tokens' in tables


def test_phase_iii_tables_exist():
    """Verify Phase III tables were created additively"""
    import sqlite3
    conn = sqlite3.connect('todo_app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [t[0] for t in cursor.fetchall()]
    conn.close()

    # Phase III tables
    assert 'conversations' in tables
    assert 'messages' in tables


def test_settings_load():
    """Verify settings configuration loads correctly"""
    from src.core.config import settings

    assert settings is not None
    assert settings.DATABASE_URL is not None
    assert settings.SECRET_KEY is not None
    assert settings.AGENT_MODEL == "gpt-4-turbo"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
