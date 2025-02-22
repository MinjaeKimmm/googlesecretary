import asyncio
import httpx
from datetime import datetime

async def test_auth_endpoint():
    print("\n=== Testing Auth Endpoint ===")
    
    # Test data with test_mode flag
    test_token = {
        "token": "test_google_token",
        "refresh_token": "test_refresh_token",
        "test_mode": True  # Enable test mode
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/auth/token",
                json=test_token
            )
            
            print(f"Status Code: {response.status_code}")
            print("Response:")
            response_data = response.json()
            print(f"  Access Token: {response_data['access_token']}")
            print(f"  User Email: {response_data['user']['email']}")
            print(f"  User Name: {response_data['user']['name']}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("Starting test...")
    asyncio.run(test_auth_endpoint())
