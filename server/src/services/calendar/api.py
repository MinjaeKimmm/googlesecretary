import requests
from typing import Dict, Any, Optional
from src.services.database.mongodb import get_db

class CalendarAPI:
    """Direct Google Calendar API interactions."""
    
    BASE_URL = "https://www.googleapis.com/calendar/v3"
    
    @staticmethod
    def _get_headers(access_token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

    @staticmethod
    async def _get_user_token(user_email: str) -> Optional[str]:
        db = await get_db()
        user = await db.users.find_one({"email": user_email})
        return user.get("access_token") if user else None

    @classmethod
    async def list_calendars(cls, user_email: str) -> Dict[str, Any]:
        """List all calendars for a user."""
        access_token = await cls._get_user_token(user_email)
        if not access_token:
            raise ValueError("User not found or not authenticated")

        response = requests.get(
            f"{cls.BASE_URL}/users/me/calendarList",
            headers=cls._get_headers(access_token)
        )
        response.raise_for_status()
        return response.json()

    @classmethod
    async def get_calendar_timezone(cls, user_email: str, calendar_id: str) -> str:
        """Get timezone for a specific calendar."""
        access_token = await cls._get_user_token(user_email)
        if not access_token:
            raise ValueError("User not found or not authenticated")

        response = requests.get(
            f"{cls.BASE_URL}/calendars/{calendar_id}",
            headers=cls._get_headers(access_token)
        )
        response.raise_for_status()
        return response.json().get("timeZone", "UTC")

    @classmethod
    async def list_events(cls, user_email: str, calendar_id: str,
                   time_min: str, time_max: str) -> Dict[str, Any]:
        """List events in a calendar."""
        access_token = await cls._get_user_token(user_email)
        if not access_token:
            raise ValueError("User not found or not authenticated")

        params = {
            "timeMin": time_min,
            "timeMax": time_max,
            "singleEvents": True,
            "orderBy": "startTime"
        }

        response = requests.get(
            f"{cls.BASE_URL}/calendars/{calendar_id}/events",
            headers=cls._get_headers(access_token),
            params=params
        )
        response.raise_for_status()
        return response.json()

    @classmethod
    async def create_event(cls, user_email: str, calendar_id: str,
                    event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new event."""
        access_token = await cls._get_user_token(user_email)
        if not access_token:
            raise ValueError("User not found or not authenticated")

        headers = cls._get_headers(access_token)
        headers["Content-Type"] = "application/json"

        response = requests.post(
            f"{cls.BASE_URL}/calendars/{calendar_id}/events",
            headers=headers,
            json=event_data
        )
        response.raise_for_status()
        return response.json()

    @classmethod
    async def delete_event(cls, user_email: str, calendar_id: str,
                    event_id: str) -> bool:
        """Delete an event."""
        access_token = await cls._get_user_token(user_email)
        if not access_token:
            raise ValueError("User not found or not authenticated")

        response = requests.delete(
            f"{cls.BASE_URL}/calendars/{calendar_id}/events/{event_id}",
            headers=cls._get_headers(access_token)
        )
        return response.status_code == 204
