import requests
import json

# Login first
login_response = requests.post(
    "http://localhost:8000/api/v1/login",
    json={"email": "test@chatbot.com", "password": "TestPassword123!"}
)

print("Login Status:", login_response.status_code)
token = login_response.json().get("access_token")
print("Token:", token[:30] + "...")

# Test chat
headers = {"Authorization": f"Bearer {token}"}
chat_response = requests.post(
    "http://localhost:8000/api/v1/chat",
    headers=headers,
    json={"message": "Hello"}
)

print("\nChat Status:", chat_response.status_code)
print("Chat Response:")
print(json.dumps(chat_response.json(), indent=2))
