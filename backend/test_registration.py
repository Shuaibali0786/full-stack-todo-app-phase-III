#!/usr/bin/env python3
"""
Test script to debug registration issues
"""
import asyncio
import sys
import traceback

# Add src to path
sys.path.insert(0, './src')

from src.core.database import get_session
from src.models.user import UserBase
from src.services.auth_service import AuthService


async def test_registration():
    """Test user registration directly"""
    print("=" * 60)
    print("TESTING USER REGISTRATION")
    print("=" * 60)

    try:
        # Get a session
        async for session in get_session():
            print("\n[1/2] Creating user data...")
            user_data = UserBase(
                email="testuser@example.com",
                first_name="Test",
                last_name="User"
            )
            print(f"[OK] User data created: {user_data}")

            print("\n[2/2] Registering user...")
            user = await AuthService.register_user_no_tokens(
                session,
                user_data,
                "testpassword123"
            )
            print(f"[OK] User registered successfully!")
            print(f"   - ID: {user.id}")
            print(f"   - Email: {user.email}")
            print(f"   - First Name: {user.first_name}")
            print(f"   - Last Name: {user.last_name}")
            print(f"   - Created At: {user.created_at}")

            return True

    except Exception as e:
        print(f"\n[FAILED] Registration failed!")
        print(f"   Error Type: {type(e).__name__}")
        print(f"   Error Message: {str(e)}")
        print(f"\n   Full Traceback:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_registration())
    print("\n" + "=" * 60)
    if success:
        print("[OK] TEST PASSED")
    else:
        print("[FAILED] TEST FAILED")
    print("=" * 60)
    sys.exit(0 if success else 1)
