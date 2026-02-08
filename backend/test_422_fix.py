"""
Test to verify 422 error is fixed
"""
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

print("Testing Dashboard API Endpoints...")
print("=" * 60)

# Test 1: GET /api/v1/tasks (no trailing slash)
print("\n1. Testing GET /api/v1/tasks (no trailing slash)")
response = client.get("/api/v1/tasks?sort=created_at&order=desc&limit=25&offset=0")
print(f"   Status: {response.status_code}")
print(f"   Expected: 401 (not authenticated) NOT 422")
print(f"   Result: {'PASS' if response.status_code == 401 else 'FAIL'}")

# Test 2: GET /api/v1/tasks/ (with trailing slash)
print("\n2. Testing GET /api/v1/tasks/ (with trailing slash)")
response = client.get("/api/v1/tasks/?sort=created_at&order=desc&limit=25&offset=0")
print(f"   Status: {response.status_code}")
print(f"   Expected: 401 (not authenticated) NOT 422")
print(f"   Result: {'PASS' if response.status_code == 401 else 'FAIL'}")

# Test 3: GET /api/v1/tags (no trailing slash)
print("\n3. Testing GET /api/v1/tags (no trailing slash)")
response = client.get("/api/v1/tags")
print(f"   Status: {response.status_code}")
print(f"   Expected: 401 (not authenticated) NOT 422")
print(f"   Result: {'PASS' if response.status_code == 401 else 'FAIL'}")

# Test 4: GET /api/v1/tags/ (with trailing slash)
print("\n4. Testing GET /api/v1/tags/ (with trailing slash)")
response = client.get("/api/v1/tags/")
print(f"   Status: {response.status_code}")
print(f"   Expected: 401 (not authenticated) NOT 422")
print(f"   Result: {'PASS' if response.status_code == 401 else 'FAIL'}")

# Test 5: GET /api/v1/priorities (no trailing slash)
print("\n5. Testing GET /api/v1/priorities (no trailing slash)")
response = client.get("/api/v1/priorities")
print(f"   Status: {response.status_code}")
print(f"   Expected: 401 (not authenticated) NOT 422")
print(f"   Result: {'PASS' if response.status_code == 401 else 'FAIL'}")

# Test 6: GET /api/v1/priorities/ (with trailing slash)
print("\n6. Testing GET /api/v1/priorities/ (with trailing slash)")
response = client.get("/api/v1/priorities/")
print(f"   Status: {response.status_code}")
print(f"   Expected: 401 (not authenticated) NOT 422")
print(f"   Result: {'PASS' if response.status_code == 401 else 'FAIL'}")

print("\n" + "=" * 60)
print("All tests completed!")
print("\nNote: 401 responses are expected (not authenticated)")
print("What we're testing: NO 422 errors (Unprocessable Entity)")
print("\nIf all tests show 401 instead of 422, the fix is working!")
