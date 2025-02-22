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

async def get_calendar_service(email: str, access_token: str, refresh_token: str = None) -> CalendarService:
    """Get calendar service instance for a user."""
    print(f"Getting calendar service for email: {email}")
    try:
        # First, update the tokens in the database
        from src.services.database.mongodb import update_user_tokens
        await update_user_tokens(email, access_token, refresh_token)
        print(f"Updated database with new tokens for user: {email}")
        
        # Get the user with updated tokens
        existing_user = await get_user_by_email(email)
        if not existing_user:
            # If user doesn't exist, create new user
            from src.models.user import User, ServiceSetup
            user = User(
                email=email,
                access_token=access_token,
                refresh_token=refresh_token,
                services={"calendar": ServiceSetup(is_setup=True)}
            )
        else:
            # Use existing user but with updated tokens
            existing_user.access_token = access_token
            if refresh_token:
                existing_user.refresh_token = refresh_token
            if "calendar" not in existing_user.services:
                existing_user.services["calendar"] = ServiceSetup(is_setup=True)
            else:
                existing_user.services["calendar"].is_setup = True
            user = existing_user
        
        print(f"User configured: {user}")
        return CalendarService(user)
    except Exception as e:
        print(f"Error in get_calendar_service: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize calendar service: {str(e)}")

@router.post("/list_calendars", response_model=CalendarList)
async def list_calendars(request: CalendarListRequest):
    """List all calendars for a user."""
    print(f"List calendars request: {request}")
    try:
        calendar_service = await get_calendar_service(
            email=request.email,
            access_token=request.access_token,
            refresh_token=request.refresh_token
        )
        calendars = await calendar_service.list_calendars()
        return CalendarList(
            email=request.email,
            calendar_names=calendars
        )
    except HTTPException as he:
        print(f"HTTP error in list_calendars: {str(he)}")
        raise he
    except Exception as e:
        print(f"Unexpected error in list_calendars: {str(e)}")
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
    print(f"Chat request received: {request}")
    print(f"Request details - email: {request.user_email}, has_access_token: {bool(request.access_token)}, has_refresh_token: {bool(request.refresh_token)}")
    try:
        calendar_service = await get_calendar_service(
            email=request.user_email,
            access_token=request.access_token,
            refresh_token=request.refresh_token
        )
        
        response = await calendar_service.process_chat(
            user_message=request.user_message,
            calendar_id=request.calendar_id,
            user_email=request.user_email  # Pass the user_email from the request
        )
        
        print(f"Chat response: {response}")
        return ChatResponse(answer=response)
        
    except HTTPException as he:
        print(f"HTTP error in chat: {str(he)}")
        raise he
    except Exception as e:
        print(f"Unexpected error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
