from .api import CalendarAPI

def get_calendar_timezone(user_email: str, calendar_id: str) -> str:
    """Get the timezone for a specific calendar."""
    try:
        return CalendarAPI.get_calendar_timezone(user_email, calendar_id)
    except Exception as e:
        print(f"Error getting calendar timezone: {str(e)}")
        return "UTC"  # Default to UTC if timezone cannot be determined
