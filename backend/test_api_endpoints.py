"""
Test script to verify all API endpoints work correctly
Tests GET and POST methods for tasks, priorities, and tags
"""
import asyncio
import httpx
import sys
from pathlib import Path

# Add backend src to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir / "src"))

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Test credentials (update with your actual test user)
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123"
}


async def test_endpoints():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("=" * 60)
        print("API Endpoint Testing")
        print("=" * 60)

        # Step 1: Login to get auth token
        print("\n1. Testing authentication...")
        try:
            login_response = await client.post(
                f"{API_BASE}/login",
                json=TEST_USER
            )
            if login_response.status_code == 200:
                data = login_response.json()
                access_token = data.get("access_token")
                print(f"   ✅ Login successful")
                print(f"   Token: {access_token[:20]}...")
            else:
                print(f"   ❌ Login failed: {login_response.status_code}")
                print(f"   Response: {login_response.text}")
                print("\n   Note: Update TEST_USER credentials in this script")
                return
        except Exception as e:
            print(f"   ❌ Login error: {str(e)}")
            return

        # Set auth headers
        headers = {"Authorization": f"Bearer {access_token}"}

        # Step 2: Test GET /priorities
        print("\n2. Testing GET /api/v1/priorities...")
        try:
            response = await client.get(f"{API_BASE}/priorities", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                priorities = response.json()
                print(f"   ✅ Success - Found {len(priorities)} priorities")
                for p in priorities[:3]:  # Show first 3
                    print(f"      - {p['name']} (value: {p['value']})")
            else:
                print(f"   ❌ Failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

        # Step 3: Test GET /tags
        print("\n3. Testing GET /api/v1/tags...")
        try:
            response = await client.get(f"{API_BASE}/tags", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                tags = response.json()
                print(f"   ✅ Success - Found {len(tags)} tags")
                for t in tags[:3]:  # Show first 3
                    print(f"      - {t['name']}")
            else:
                print(f"   ❌ Failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

        # Step 4: Test GET /tasks
        print("\n4. Testing GET /api/v1/tasks...")
        try:
            response = await client.get(f"{API_BASE}/tasks", headers=headers)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                tasks = data.get('tasks', [])
                total = data.get('total', 0)
                print(f"   ✅ Success - Found {total} total tasks")
                print(f"   Returned {len(tasks)} tasks in this page")
                for t in tasks[:3]:  # Show first 3
                    print(f"      - {t['title']}")
            else:
                print(f"   ❌ Failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

        # Step 5: Test POST /tasks (without trailing slash)
        print("\n5. Testing POST /api/v1/tasks (no trailing slash)...")
        test_task = {
            "title": "Test Task from API Test",
            "description": "This task was created by the test script",
            "priority_id": None,
            "due_date": None,
            "reminder_time": None,
            "tag_ids": []
        }
        try:
            response = await client.post(
                f"{API_BASE}/tasks",  # No trailing slash
                json=test_task,
                headers=headers
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                task = response.json()
                print(f"   ✅ Success - Created task: {task['title']}")
                print(f"   Task ID: {task['id']}")
                created_task_id = task['id']
            else:
                print(f"   ❌ Failed: {response.text}")
                created_task_id = None
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            created_task_id = None

        # Step 6: Test POST /tasks/ (with trailing slash)
        print("\n6. Testing POST /api/v1/tasks/ (with trailing slash)...")
        test_task2 = {
            "title": "Test Task 2 from API Test",
            "description": "Testing with trailing slash",
            "priority_id": None,
            "due_date": None,
            "reminder_time": None,
            "tag_ids": []
        }
        try:
            response = await client.post(
                f"{API_BASE}/tasks/",  # With trailing slash
                json=test_task2,
                headers=headers
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                task = response.json()
                print(f"   ✅ Success - Created task: {task['title']}")
                print(f"   Task ID: {task['id']}")
            else:
                print(f"   ❌ Failed: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

        # Step 7: Clean up - delete test task
        if created_task_id:
            print(f"\n7. Cleaning up - deleting test task {created_task_id}...")
            try:
                response = await client.delete(
                    f"{API_BASE}/tasks/{created_task_id}",
                    headers=headers
                )
                if response.status_code == 200:
                    print(f"   ✅ Test task deleted")
                else:
                    print(f"   ⚠️  Failed to delete: {response.text}")
            except Exception as e:
                print(f"   ⚠️  Delete error: {str(e)}")

        print("\n" + "=" * 60)
        print("Testing complete!")
        print("=" * 60)


if __name__ == "__main__":
    print("\n🔧 Starting API endpoint tests...")
    print("   Make sure the backend is running on http://localhost:8000")
    print()
    asyncio.run(test_endpoints())
