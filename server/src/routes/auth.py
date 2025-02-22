from fastapi import APIRouter, Depends, HTTPException, Request
from datetime import datetime, timedelta
from src.models.user import User, UserInDB, ServiceSetup
from src.services.database import get_db
from src.utils.auth import verify_google_token, refresh_google_token, get_current_user
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from src.services.database.mongodb import get_service_status
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

    # Create or update user with default service setup
    current_time = datetime.utcnow()
    user_data = {
        "email": user_info["email"],
        "name": user_info.get("name"),
        "picture": user_info.get("picture"),
        "access_token": token_request.token,
        "refresh_token": token_request.refresh_token,
        "token_expiry": token_expiry,
        "created_at": current_time,
        "updated_at": current_time,
        "services": {
            "calendar": {
                "is_setup": True,  # Calendar is set up by default since we have tokens
                "last_setup_time": current_time,
                "scope_version": "v1"
            },
            "email": {
                "is_setup": False,
                "last_setup_time": None,
                "scope_version": "v1"
            },
            "drive": {
                "is_setup": False,
                "last_setup_time": None,
                "scope_version": "v1"
            }
        }
    }

    print(f"User data before save: {user_data}")
    
    # Try to find existing user
    existing_user = await db.users.find_one({"email": user_info["email"]})
    if existing_user:
        print(f"Found existing user: {existing_user}")
        # Update existing user while preserving service setup state
        update_data = {
            "email": user_data["email"],
            "name": user_data["name"],
            "picture": user_data["picture"],
            "access_token": user_data["access_token"],
            "refresh_token": user_data["refresh_token"],
            "token_expiry": user_data["token_expiry"],
            "updated_at": user_data["updated_at"],
        }
        
        # Only update service setup if not already set
        for service_name in ["calendar", "email", "drive"]:
            service_path = f"services.{service_name}"
            if service_path not in existing_user or not existing_user[service_path].get("is_setup"):
                update_data[f"{service_path}.is_setup"] = user_data["services"][service_name]["is_setup"]
                update_data[f"{service_path}.last_setup_time"] = user_data["services"][service_name]["last_setup_time"]
                update_data[f"{service_path}.scope_version"] = user_data["services"][service_name]["scope_version"]
        
        # Update the user
        await db.users.update_one(
            {"email": user_info["email"]},
            {"$set": update_data}
        )
        user_data["id"] = str(existing_user["_id"])
    else:
        print("Creating new user")
        # Insert new user with complete data
        result = await db.users.insert_one(user_data)
        user_data["id"] = str(result.inserted_id)
        print(f"Created new user with ID: {user_data['id']}")
    
    # Verify the saved user
    saved_user = await db.users.find_one({"email": user_info["email"]})
    print(f"Saved user data: {saved_user}")

    return TokenResponse(
        access_token=token_request.token,
        user=UserInDB(**user_data)
    )

@router.post("/check-service-status")
async def check_service_status(
    request: Request,
    service: str = None,
    current_user: User = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    print(f"\n=== Check service status endpoint called ===\nService: {service}\nUser: {current_user}")
    try:
        # Verify user exists in database
        user_doc = await db.users.find_one({"email": current_user.email})
        if not user_doc:
            print(f"User {current_user.email} not found in database")
            raise HTTPException(
                status_code=404,
                detail=f"User {current_user.email} not found"
            )

        # Get service status
        status = await get_service_status(current_user.email, service)
        print(f"Service status: {status}")
        
        # If no status found, return default status
        if not status:
            print(f"No service status found for {current_user.email}, returning default")
            status = {
                "calendar": {
                    "is_setup": True,
                    "last_setup_time": datetime.utcnow(),
                    "scope_version": "v1"
                },
                "email": {
                    "is_setup": False,
                    "last_setup_time": None,
                    "scope_version": "v1"
                },
                "drive": {
                    "is_setup": False,
                    "last_setup_time": None,
                    "scope_version": "v1"
                }
            }
            
            # Update database with default status
            await db.users.update_one(
                {"email": current_user.email},
                {"$set": {"services": status}}
            )

        return {
            "email": current_user.email,
            "services": status
        }
    except HTTPException as he:
        print(f"HTTP Exception in check_service_status: {he}")
        raise he
    except Exception as e:
        print(f"Unexpected error in check_service_status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get service status: {str(e)}"
        )
