from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from typing import List, Dict
import pytz

from src.config.settings import get_settings
from src.agents.calendar_agent import CalendarAgent

class CalendarService:
    def __init__(self, user):
        self.creds = Credentials(
            token=user.access_token,
            refresh_token=user.refresh_token,
            client_id=get_settings().google_client_id,
            client_secret=get_settings().google_client_secret,
            token_uri="https://oauth2.googleapis.com/token"
        )
        self.service = build('calendar', 'v3', credentials=self.creds)
        self.agent = CalendarAgent()

    async def list_calendars(self) -> List[Dict]:
        """List all available calendars for the user."""
        try:
            calendar_list = self.service.calendarList().list().execute()
            calendars = []
            for calendar in calendar_list.get('items', []):
                calendars.append({
                    'id': calendar['id'],
                    'summary': calendar['summary']
                })
            return calendars
        except Exception as e:
            print(f"Error listing calendars: {str(e)}")
            return []

    async def list_events(self, calendar_id: str, time_min: datetime = None, 
                         time_max: datetime = None) -> List[Dict]:
        """List events from a specific calendar."""
        if not time_min:
            time_min = datetime.now(pytz.UTC)
        if not time_max:
            time_max = time_min + timedelta(days=7)

        try:
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min.isoformat(),
                timeMax=time_max.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = []
            for event in events_result.get('items', []):
                start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date'))
                end = event.get('end', {}).get('dateTime', event.get('end', {}).get('date'))
                events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No title'),
                    'start': start,
                    'end': end,
                    'description': event.get('description', ''),
                    'location': event.get('location', '')
                })
            return events
        except Exception as e:
            print(f"Error listing events: {str(e)}")
            return []

    async def process_chat(self, user_message: str, calendar_id: str, user_email: str = None) -> str:
        """Process a chat message using the calendar agent."""
        try:
            # Get recent events for context
            events = await self.list_events(calendar_id)
            # Use the user_email from the request or a default
            user_email = user_email or "user@example.com"
            return await self.agent.process_message(user_email, user_message, calendar_id)
        except Exception as e:
            print(f"Error processing chat: {str(e)}")
            return "I apologize, but I encountered an error while processing your request."
