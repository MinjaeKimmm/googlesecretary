from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from src.models.user import User, UserInDB, ServiceSetup
from src.services.database import get_db
from src.utils.auth import verify_google_token, refresh_google_token
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
import os

router = APIRouter()

class TokenRequest(BaseModel):
    token: str
    refresh_token: str
    test_mode: bool = False  # Add test mode flag

class TokenResponse(BaseModel):
    access_token: str
    user: UserInDB

@router.post("/token", response_model=TokenResponse)
async def handle_token(
    token_request: TokenRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    print("\n=== Token endpoint called ===")
    print(f"Token request: {token_request}")
    # If in test mode, use mock data
    if token_request.test_mode:
        user_info = {
            "email": "test@example.com",
            "name": "Test User",
            "picture": "https://example.com/picture.jpg"
        }
    else:
        print("Verifying Google token...")
        # Verify token
        user_info = await verify_google_token(token_request.token)
        print(f"Google token verification result: {user_info}")
        if not user_info:
            print("Token verification failed!")
            raise HTTPException(status_code=401, detail="Invalid token")

    # Calculate token expiry (1 hour from now)
    token_expiry = datetime.utcnow() + timedelta(hours=1)

    # Create service setup objects
    calendar_service = ServiceSetup(
        is_setup=True,
        last_setup_time=datetime.utcnow(),
        scope_version="v1"
    )
    email_service = ServiceSetup(
        is_setup=False,
        last_setup_time=None,
        scope_version="v1"
    )
    drive_service = ServiceSetup(
        is_setup=False,
        last_setup_time=None,
        scope_version="v1"
    )

    # Create or update user
    user_data = {
        "email": user_info["email"],
        "name": user_info.get("name"),
        "picture": user_info.get("picture"),
        "access_token": token_request.token,
        "refresh_token": token_request.refresh_token,
        "token_expiry": token_expiry,
        "updated_at": datetime.utcnow(),
        "services": {
            "calendar": {
                "is_setup": calendar_service.is_setup,
                "last_setup_time": calendar_service.last_setup_time,
                "scope_version": calendar_service.scope_version
            },
            "email": {
                "is_setup": email_service.is_setup,
                "last_setup_time": email_service.last_setup_time,
                "scope_version": email_service.scope_version
            },
            "drive": {
                "is_setup": drive_service.is_setup,
                "last_setup_time": drive_service.last_setup_time,
                "scope_version": drive_service.scope_version
            }
        }
    }

    print(f"User data before save: {user_data}")
    
    # Try to find existing user
    existing_user = await db.users.find_one({"email": user_info["email"]})
    if existing_user:
        print(f"Found existing user: {existing_user}")
        # Update existing user - use dot notation for nested fields
        update_data = {
            "email": user_data["email"],
            "name": user_data["name"],
            "picture": user_data["picture"],
            "access_token": user_data["access_token"],
            "refresh_token": user_data["refresh_token"],
            "token_expiry": user_data["token_expiry"],
            "updated_at": user_data["updated_at"],
            "services.calendar.is_setup": user_data["services"]["calendar"]["is_setup"],
            "services.calendar.last_setup_time": user_data["services"]["calendar"]["last_setup_time"],
            "services.calendar.scope_version": user_data["services"]["calendar"]["scope_version"],
            "services.email.is_setup": user_data["services"]["email"]["is_setup"],
            "services.email.last_setup_time": user_data["services"]["email"]["last_setup_time"],
            "services.email.scope_version": user_data["services"]["email"]["scope_version"],
            "services.drive.is_setup": user_data["services"]["drive"]["is_setup"],
            "services.drive.last_setup_time": user_data["services"]["drive"]["last_setup_time"],
            "services.drive.scope_version": user_data["services"]["drive"]["scope_version"]
        }
        await db.users.update_one(
            {"email": user_info["email"]},
            {"$set": update_data}
        )
        user_data["id"] = str(existing_user["_id"])
    else:
        print("Creating new user")
        # Insert new user
        result = await db.users.insert_one(user_data)
        user_data["id"] = str(result.inserted_id)
    
    # Verify the saved user
    saved_user = await db.users.find_one({"email": user_info["email"]})
    print(f"Saved user data: {saved_user}")

    return TokenResponse(
        access_token=token_request.token,
        user=UserInDB(**user_data)
    )
