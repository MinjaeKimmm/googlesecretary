from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from typing import List, Dict
from zoneinfo import ZoneInfo

from src.config.settings import get_settings
from src.agents.calendar_agent import CalendarAgent
from src.utils.timezone import to_utc, to_local, format_local_time, DEFAULT_TIMEZONE

class CalendarService:
    def __init__(self, user):
        self.user = user
        print(f"Initializing calendar service for user: {user.email}")
        print(f"Access token available: {bool(user.access_token)}, Refresh token available: {bool(user.refresh_token)}")
        
        try:
            print(f"Creating credentials with client_id: {bool(get_settings().google_client_id)}, client_secret: {bool(get_settings().google_client_secret)}")
            self.creds = Credentials(
                token=user.access_token,
                refresh_token=user.refresh_token,
                client_id=get_settings().google_client_id,
                client_secret=get_settings().google_client_secret,
                token_uri="https://oauth2.googleapis.com/token",
                scopes=['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/calendar.events']
            )
            print(f"Credentials created with token: {bool(self.creds.token)}, refresh_token: {bool(self.creds.refresh_token)}")
            print("Credentials created successfully")
            
            self.service = build('calendar', 'v3', credentials=self.creds)
            print("Calendar service built successfully")
            
            self.agent = CalendarAgent()
            print("Calendar agent initialized")
            
        except Exception as e:
            print(f"Error initializing calendar service: {str(e)}")
            raise
        
    async def _check_token_refresh(self):
        """Check if token was refreshed and update database if needed."""
        if self.creds.token != self.user.access_token:
            from src.services.database.mongodb import update_user_tokens
            await update_user_tokens(
                email=self.user.email,
                access_token=self.creds.token,
                refresh_token=self.creds.refresh_token,
                token_expiry=self.creds.expiry
            )

    async def list_calendars(self) -> List[Dict]:
        """List all available calendars for the user."""
        try:
            calendar_list = self.service.calendarList().list().execute()
            await self._check_token_refresh()
            
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
            time_min = datetime.now(ZoneInfo("UTC"))
        if not time_max:
            time_max = time_min + timedelta(days=7)

        try:
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min.isoformat(),
                timeMax=time_max.isoformat(),
                singleEvents=True,
                orderBy='startTime',
                timeZone=DEFAULT_TIMEZONE  # Request times in local timezone
            ).execute()
            
            events = []
            for event in events_result.get('items', []):
                start_dt = event.get('start', {}).get('dateTime')
                end_dt = event.get('end', {}).get('dateTime')
                
                # Convert to datetime objects if they exist
                if start_dt:
                    start_dt = datetime.fromisoformat(start_dt.replace('Z', '+00:00'))
                    start_local = format_local_time(start_dt)
                else:
                    start_local = event.get('start', {}).get('date', '')
                    
                if end_dt:
                    end_dt = datetime.fromisoformat(end_dt.replace('Z', '+00:00'))
                    end_local = format_local_time(end_dt)
                else:
                    end_local = event.get('end', {}).get('date', '')
                
                events.append({
                    'id': event['id'],
                    'summary': event.get('summary', 'No title'),
                    'start': start_local,
                    'end': end_local,
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
