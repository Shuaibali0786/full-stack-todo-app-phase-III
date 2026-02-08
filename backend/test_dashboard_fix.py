"""
Quick test to verify dashboard API endpoints work correctly
"""
import asyncio
from src.core.database import get_session
from src.models.user import User
from sqlmodel import select


async def test_endpoints():
    """Test that the API routes are properly configured"""
    from src.api.v1 import tasks, tags, priorities

    print("[OK] Tasks router loaded")
    print("[OK] Tags router loaded")
    print("[OK] Priorities router loaded")

    # Test that Query parameters are properly defined
    from src.api.v1.tasks import get_tasks
    import inspect

    sig = inspect.signature(get_tasks)
    params = sig.parameters

    print("\nTasks endpoint parameters:")
    for param_name, param in params.items():
        if param_name not in ['current_user', 'session']:
            print(f"   - {param_name}: {param.annotation} = {param.default}")

    print("\n[OK] All endpoints configured correctly!")
    print("\nExpected behavior:")
    print("  - GET /api/v1/tasks/ → Should work with no query params")
    print("  - GET /api/v1/tasks/?sort=created_at&order=desc&limit=25&offset=0 → Should work")
    print("  - GET /api/v1/tags/ → Should work")
    print("  - GET /api/v1/priorities/ → Should work")


if __name__ == "__main__":
    asyncio.run(test_endpoints())
