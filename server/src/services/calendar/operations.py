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
    timezone = await get_calendar_timezone(user_email, calendar_id)
    
    event_data = {
        "summary": f"{event_name} (created by Assistant)",
        "start": {
            "dateTime": start_datetime,
            "timeZone": timezone,
        },
        "end": {
            "dateTime": end_datetime,
            "timeZone": timezone,
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
