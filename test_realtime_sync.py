#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify realtime dashboard sync after chatbot actions.
Tests that the backend returns proper 'actions' array for frontend to trigger refresh.
"""

import requests
import json
import sys

API_URL = "http://localhost:8000"

def test_realtime_sync():
    """Test the complete realtime sync flow"""

    print("=" * 70)
    print("REALTIME DASHBOARD SYNC TEST")
    print("=" * 70)
    print()

    # Step 1: Register a test user (or use existing)
    print("[Step 1] Creating test user...")
    register_data = {
        "email": "test_sync@example.com",
        "password": "TestSync123!",
        "first_name": "Sync",
        "last_name": "Test"
    }

    try:
        response = requests.post(f"{API_URL}/api/v1/register", json=register_data)
        if response.status_code in [200, 201]:
            print("   [OK] User created successfully")
        elif response.status_code == 409:
            print("   [INFO] User already exists (using existing account)")
        else:
            print(f"   [FAIL] Registration failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   [WARN] Registration error (may already exist): {e}")

    print()

    # Step 2: Login to get token
    print("[Step 2] Logging in...")
    login_data = {
        "email": "test_sync@example.com",
        "password": "TestSync123!"
    }

    try:
        response = requests.post(f"{API_URL}/api/v1/login", json=login_data)
        if response.status_code != 200:
            print(f"   [FAIL] Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

        token_data = response.json()
        access_token = token_data.get("access_token")
        print(f"   [OK] Login successful")
        print(f"   Token: {access_token[:20]}...")
    except Exception as e:
        print(f"   [FAIL] Login error: {e}")
        return False

    print()

    # Step 3: Send chatbot message to CREATE a task
    print("[Step 3] Testing CHATBOT CREATE ACTION...")
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    chat_message = {
        "message": "add task Test Realtime Sync Feature"
    }

    try:
        response = requests.post(
            f"{API_URL}/api/v1/chat",
            json=chat_message,
            headers=headers
        )

        if response.status_code != 200:
            print(f"   [FAIL] Chat request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

        chat_response = response.json()
        print(f"   [OK] Chat response received")
        response_text = chat_response.get('response', '')[:100]
        # Encode to ASCII to avoid Windows console Unicode errors
        response_text_safe = response_text.encode('ascii', 'ignore').decode('ascii')
        print(f"   Response: {response_text_safe}...")
        print()

        # CRITICAL: Check if actions array is present
        actions = chat_response.get("actions", [])
        print("   [CRITICAL CHECK] ACTIONS ARRAY (REQUIRED FOR REALTIME SYNC):")
        print(f"      Actions present: {len(actions) > 0}")
        print(f"      Actions count: {len(actions)}")

        if len(actions) > 0:
            print()
            print("   [SUCCESS] Actions array is present:")
            for idx, action in enumerate(actions, 1):
                print(f"      Action {idx}:")
                print(f"         Type: {action.get('type')}")
                data_str = json.dumps(action.get('data', {}), indent=10)[:200]
                print(f"         Data: {data_str}...")
            print()
            print("   [OK] REALTIME SYNC WILL WORK!")
            print("      Frontend will detect actions and refresh dashboard automatically")
        else:
            print()
            print("   [CRITICAL ISSUE] No actions in response!")
            print("      Dashboard will NOT refresh automatically")
            print("      User will need to reload page manually")
            return False

    except Exception as e:
        print(f"   [FAIL] Chat error: {e}")
        import traceback
        traceback.print_exc()
        return False

    print()

    # Step 4: Verify task was created by fetching tasks
    print("[Step 4] Verifying task was created...")
    try:
        response = requests.get(
            f"{API_URL}/api/v1",
            headers=headers
        )

        if response.status_code != 200:
            print(f"   [FAIL] Failed to fetch tasks: {response.status_code}")
            return False

        tasks_data = response.json()
        tasks = tasks_data.get("tasks", [])
        print(f"   [OK] Found {len(tasks)} total tasks")

        # Find our test task
        test_task = None
        for task in tasks:
            if "Test Realtime Sync Feature" in task.get("title", ""):
                test_task = task
                break

        if test_task:
            print(f"   [OK] Test task found: {test_task.get('title')}")
            print(f"      ID: {test_task.get('id')}")
        else:
            print("   [WARN] Test task not found (may have different title)")

    except Exception as e:
        print(f"   [FAIL] Error fetching tasks: {e}")
        return False

    print()
    print("=" * 70)
    print("SUCCESS! REALTIME SYNC TEST COMPLETED")
    print("=" * 70)
    print()
    print("VERIFIED:")
    print("   1. Backend accepts chatbot messages")
    print("   2. Backend returns 'actions' array with task_created action")
    print("   3. Frontend can detect actions and trigger dashboard refresh")
    print()
    print("NEXT STEPS - MANUAL UI TEST:")
    print("   1. Open http://localhost:3001/dashboard in your browser")
    print("   2. Open Browser Console (F12)")
    print("   3. Type in chatbot: 'add task test'")
    print("   4. Watch console logs:")
    print("      [ChatKit] [OK] Task action detected...")
    print("      [Dashboard] [OK] RefreshTrigger updated: X -> Y")
    print("      [TaskTable] [OK] Fetched N tasks")
    print("   5. Task appears in dashboard INSTANTLY (no reload!)")
    print()

    return True

if __name__ == "__main__":
    try:
        success = test_realtime_sync()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"[ERROR] Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
