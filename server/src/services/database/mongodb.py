from motor.motor_asyncio import AsyncIOMotorClient
from src.config.settings import get_settings
from datetime import datetime

settings = get_settings()
client = None
db = None

async def init_db():
    global client, db
    if client is None:
        client = AsyncIOMotorClient(settings.mongodb_uri)
        db = client[settings.mongodb_database]

async def get_db():
    if client is None:
        await init_db()
    return db

async def close_db():
    if client is not None:
        client.close()

async def update_user_tokens(email: str, access_token: str, refresh_token: str = None, token_expiry: datetime = None):
    """Update user's OAuth tokens in database."""
    db_instance = await get_db()
    update_data = {"access_token": access_token}
    
    if refresh_token:
        update_data["refresh_token"] = refresh_token
    if token_expiry:
        update_data["token_expiry"] = token_expiry
    
    await db_instance.users.update_one(
        {"email": email},
        {"$set": update_data}
    )

async def get_user_by_email(email: str):
    """Get user from database by email."""
    print(f"Getting user by email: {email}")
    db_instance = await get_db()
    user_dict = await db_instance.users.find_one({"email": email})
    print(f"Raw user dict from MongoDB: {user_dict}")
    
    if user_dict:
        from src.models.user import User, ServiceSetup
        
        # Convert service dictionaries to ServiceSetup objects
        if "services" in user_dict:
            print(f"Services before conversion: {user_dict['services']}")
            services = {}
            for service_name, service_data in user_dict["services"].items():
                print(f"Converting service {service_name}: {service_data}")
                # Convert datetime strings to datetime objects
                if service_data.get("last_setup_time"):
                    if isinstance(service_data["last_setup_time"], str):
                        service_data["last_setup_time"] = datetime.fromisoformat(service_data["last_setup_time"].replace("Z", "+00:00"))
                services[service_name] = ServiceSetup(**service_data)
            user_dict["services"] = services
            print(f"Services after conversion: {user_dict['services']}")
        
        user = User(**user_dict)
        print(f"Final user object: {user}")
        return user
    return None
