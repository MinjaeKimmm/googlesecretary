from fastapi import APIRouter, Depends, HTTPException
from src.models.calendar import (
    CalendarListRequest, CalendarList,
    EventListRequest, EventList,
    ChatRequest, ChatResponse
)
from src.services.calendar.calendar import CalendarService
from src.models.user import User
from src.services.database.mongodb import get_user_by_email
from typing import Dict

router = APIRouter()

async def get_calendar_service(email: str) -> CalendarService:
    """Get calendar service instance for a user."""
    print(f"Getting calendar service for email: {email}")
    user = await get_user_by_email(email)
    if not user:
        print(f"User not found for email: {email}")
        raise HTTPException(status_code=404, detail="User not found")
    
    print(f"User found: {user}")
    print(f"User services: {user.services}")
    
    calendar_service = user.services.get("calendar")
    print(f"Calendar service: {calendar_service}")
    
    if not calendar_service or not calendar_service.is_setup:
        print(f"Calendar service not set up: {calendar_service}")
        raise HTTPException(status_code=400, detail="Calendar service not set up")
    
    return CalendarService(user)

@router.post("/list_calendars", response_model=CalendarList)
async def list_calendars(request: CalendarListRequest):
    """List all calendars for a user."""
    try:
        calendar_service = await get_calendar_service(request.email)
        calendars = await calendar_service.list_calendars()
        return CalendarList(
            email=request.email,
            calendar_names=calendars
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/list_events", response_model=EventList)
async def list_events(request: EventListRequest):
    """List events from a specific calendar."""
    try:
        calendar_service = await get_calendar_service(request.email)
        events = await calendar_service.list_events(request.calendar_id)
        return EventList(
            email=request.email,
            events=[f"{event['summary']} - {event['start']}" for event in events]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message about calendar events."""
    try:
        calendar_service = await get_calendar_service(request.user_email)
        response = await calendar_service.process_chat(
            request.user_message,
            request.calendar_id,
            request.user_email
        )
        return ChatResponse(answer=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
