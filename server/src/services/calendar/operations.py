from typing import List, Dict, Any
from .api import CalendarAPI
from .timezone import get_calendar_timezone

async def get_calendar_events(
    user_email: str,
    calendar_id: str,
    start_time: str,
    end_time: str,
    return_event_ids: bool = False
) -> List[str]:
    """Get formatted list of calendar events."""
    events = await CalendarAPI.list_events(user_email, calendar_id, start_time, end_time)
    
    event_list = []
    for event in events.get("items", []):
        start = event.get("start", {})
        date_info = start.get("date", start.get("dateTime"))
        
        if return_event_ids:
            event_list.append(
                f"{event.get('summary')}: {date_info} (event ID: {event.get('id')})"
            )
        else:
            event_list.append(f"{event.get('summary')}: {date_info}")
    
    return event_list

async def create_event(
    user_email: str,
    calendar_id: str,
    event_name: str,
    start_datetime: str,
    end_datetime: str
) -> Dict[str, Any]:
    """Create a new calendar event."""
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from src.utils.timezone import DEFAULT_TIMEZONE
    
    # Parse the input times (which should be in UTC)
    start_dt = datetime.fromisoformat(start_datetime.replace('Z', '+00:00'))
    end_dt = datetime.fromisoformat(end_datetime.replace('Z', '+00:00'))
    
    event_data = {
        "summary": event_name,
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": DEFAULT_TIMEZONE,  # Use KST for display
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": DEFAULT_TIMEZONE,  # Use KST for display
        },
    }
    
    return await CalendarAPI.create_event(user_email, calendar_id, event_data)

async def delete_event(user_email: str, calendar_id: str, event_id: str) -> Dict[str, str]:
    """Delete a calendar event."""
    success = await CalendarAPI.delete_event(user_email, calendar_id, event_id)
    
    if success:
        return {"message": "Event deleted successfully"}
    else:
        return {"error": "Failed to delete event"}
