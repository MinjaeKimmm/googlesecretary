from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from datetime import datetime

class ServiceSetup(BaseModel):
    is_setup: bool = False
    last_setup_time: Optional[datetime] = None
    scope_version: str = "v1"

class User(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None
    access_token: str
    refresh_token: Optional[str] = None
    token_expiry: datetime
    services: dict[str, ServiceSetup] = {
        "calendar": ServiceSetup(is_setup=False),
        "email": ServiceSetup(is_setup=False),
        "drive": ServiceSetup(is_setup=False)
    }
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

class UserInDB(User):
    id: str
