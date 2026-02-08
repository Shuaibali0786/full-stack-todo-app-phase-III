"""
Test script to verify GET /tasks endpoint fix

This script tests that:
1. Query params are optional with defaults
2. Response includes correct total count
3. No 422 errors are raised
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_tasks_endpoint_without_params():
    """Test GET /tasks without any query parameters"""
    print("\n=== Test 1: GET /tasks without params ===")

    # First, login to get token
    login_response = requests.post(
        f"{BASE_URL}/api/v1/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )

    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        print("✅ Login successful")
    else:
        print("⚠️  Login failed - you may need to create a test user first")
        print(f"   Status: {login_response.status_code}")
        print(f"   Response: {login_response.text}")
        return

    # Test GET /tasks without any params (should use defaults)
    headers = {"Authorization": f"Bearer {token}"}

    print("\n--- Request: GET /api/v1/tasks/ (no params) ---")
    response = requests.get(f"{BASE_URL}/api/v1/tasks/", headers=headers)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("\n✅ SUCCESS: Endpoint returned 200 OK")
        print(f"   Response has 'tasks' key: {'tasks' in data}")
        print(f"   Response has 'total' key: {'total' in data}")
        print(f"   Response has 'offset' key: {'offset' in data}")
        print(f"   Response has 'limit' key: {'limit' in data}")
        print(f"\n   Tasks count: {len(data.get('tasks', []))}")
        print(f"   Total count: {data.get('total', 'N/A')}")
        print(f"   Offset: {data.get('offset', 'N/A')}")
        print(f"   Limit: {data.get('limit', 'N/A')}")

        # Verify response structure
        if 'tasks' in data and 'total' in data and 'offset' in data and 'limit' in data:
            print("\n✅ Response structure is correct")
        else:
            print("\n❌ Response structure is incomplete")

    elif response.status_code == 422:
        print("\n❌ FAILED: Got 422 Unprocessable Entity")
        print(f"   This means query params validation failed")
        print(f"   Response: {response.text}")
    else:
        print(f"\n❌ FAILED: Got unexpected status {response.status_code}")
        print(f"   Response: {response.text}")


def test_tasks_endpoint_with_params():
    """Test GET /tasks with query parameters"""
    print("\n\n=== Test 2: GET /tasks with params ===")

    # Login
    login_response = requests.post(
        f"{BASE_URL}/api/v1/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )

    if login_response.status_code != 200:
        print("⚠️  Login failed")
        return

    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test with params
    params = {
        "sort": "created_at",
        "order": "desc",
        "limit": 10,
        "offset": 0
    }

    print(f"\n--- Request: GET /api/v1/tasks/ with params {params} ---")
    response = requests.get(f"{BASE_URL}/api/v1/tasks/", headers=headers, params=params)

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("\n✅ SUCCESS: Endpoint returned 200 OK")
        print(f"   Tasks count: {len(data.get('tasks', []))}")
        print(f"   Total count: {data.get('total', 'N/A')}")
        print(f"   Offset: {data.get('offset', 'N/A')}")
        print(f"   Limit: {data.get('limit', 'N/A')}")

        # Verify total is >= tasks count (because of pagination)
        if data.get('total', 0) >= len(data.get('tasks', [])):
            print("\n✅ Total count is correct (>= page tasks count)")
        else:
            print("\n❌ Total count is incorrect (should be >= page tasks count)")

    else:
        print(f"\n❌ FAILED: Got status {response.status_code}")
        print(f"   Response: {response.text}")


def main():
    print("="*60)
    print("Testing GET /tasks endpoint fix")
    print("="*60)

    try:
        test_tasks_endpoint_without_params()
        test_tasks_endpoint_with_params()

        print("\n\n" + "="*60)
        print("Tests completed!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
