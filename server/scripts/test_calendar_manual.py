import requests
import json

BASE_URL = "http://localhost:8000/api/calendar"  # Adjust if your server runs on a different port

def test_endpoints():
    # Replace with a real user email that exists in your database
    TEST_USER = {
        "email": "test@test.com",
        "calendar_id": "primary"  # or the actual calendar ID you want to test
    }

    # Test 1: List Calendars
    print("\n=== Testing List Calendars ===")
    response = requests.post(
        f"{BASE_URL}/list_calendars",
        json={"email": TEST_USER["email"]}
    )
    print(f"Status: {response.status_code}")
    print("Response:", json.dumps(response.json(), indent=2))

    # Test 2: List Events
    print("\n=== Testing List Events ===")
    response = requests.post(
        f"{BASE_URL}/list_events",
        json={
            "email": TEST_USER["email"],
            "calendar_id": TEST_USER["calendar_id"]
        }
    )
    print(f"Status: {response.status_code}")
    print("Response:", json.dumps(response.json(), indent=2))

    # Test 3: Chat
    print("\n=== Testing Chat ===")
    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "user_email": TEST_USER["email"],
            "user_message": "summarize my week",
            "calendar_id": TEST_USER["calendar_id"]
        }
    )
    print(f"Status: {response.status_code}")
    print("Response:", json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_endpoints()
