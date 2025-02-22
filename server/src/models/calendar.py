from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Calendar List Models
class CalendarListRequest(BaseModel):
    email: str
    access_token: str
    refresh_token: Optional[str] = None

class CalendarList(BaseModel):
    email: str
    calendar_names: List[dict]  # List of {calendar_id: calendar_name}

# Event Models
class EventListRequest(BaseModel):
    email: str
    calendar_id: str

class EventList(BaseModel):
    email: str
    events: List[str]  # List of formatted event strings

# Chat Models
class ChatRequest(BaseModel):
    user_email: str
    user_message: str
    calendar_id: str
    access_token: str
    refresh_token: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
