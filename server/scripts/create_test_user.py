import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta

# MongoDB connection settings
MONGODB_URI = "mongodb://localhost:27017"
MONGODB_DATABASE = "eleven"

async def create_test_user():
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[MONGODB_DATABASE]
    
    # Test user data with proper structure
    test_user = {
        "email": "test@test.com",
        "name": "Test User",
        "access_token": "fake_access_token",
        "refresh_token": "fake_refresh_token",
        "token_expiry": datetime.utcnow() + timedelta(hours=1),
        "services": {
            "calendar": {
                "is_setup": True,
                "last_setup_time": datetime.utcnow(),
                "scope_version": "v1"
            },
            "email": {
                "is_setup": False,
                "scope_version": "v1"
            },
            "drive": {
                "is_setup": False,
                "scope_version": "v1"
            }
        }
    }
    
    # Insert or update the test user
    await db.users.update_one(
        {"email": test_user["email"]},
        {"$set": test_user},
        upsert=True
    )
    
    print(f"Test user created/updated: {test_user['email']}")
    client.close()

if __name__ == "__main__":
    asyncio.run(create_test_user())
