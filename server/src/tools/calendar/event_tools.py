from typing import List, Type
from pydantic import BaseModel, Field

from .base import CalendarBaseTool
from src.services.calendar.operations import (
    get_calendar_events,
    create_event,
    delete_event
)

class CalendarEventSearchInput(BaseModel):
    """Input schema for GetCalendarEventsTool."""
    user_email: str = Field(..., description="Email of the user")
    calendar_id: str = Field(..., description="Calendar ID")
    start_date: str = Field(..., description="Start date (RFC3339 format)")
    end_date: str = Field(..., description="End date (RFC3339 format)")
    include_event_ids: bool = Field(
        default=False,
        description="Whether to include event IDs in the response"
    )

class GetCalendarEventsTool(CalendarBaseTool):
    name: str = "get_calendar_events"
    description: str = "Retrieve calendar events within a specified date range"
    args_schema: Type[CalendarEventSearchInput] = CalendarEventSearchInput

    def _run(self, *args, **kwargs):
        raise NotImplementedError("Use arun instead")

    async def _arun(self, user_email: str, calendar_id: str,
             start_date: str, end_date: str, include_event_ids: bool = False) -> List[str]:
        return await get_calendar_events(
            user_email,
            calendar_id,
            start_date,
            end_date,
            include_event_ids
        )

class CalendarCreateInput(BaseModel):
    """Input schema for CreateCalendarEventTool."""
    user_email: str = Field(..., description="Email of the user")
    calendar_id: str = Field(..., description="Calendar ID")
    event_name: str = Field(..., description="Name of the event")
    start_datetime: str = Field(..., description="Start time (RFC3339 format)")
    end_datetime: str = Field(..., description="End time (RFC3339 format)")

class CreateCalendarEventTool(CalendarBaseTool):
    name: str = "create_calendar_event"
    description: str = "Create a new calendar event"
    args_schema: Type[CalendarCreateInput] = CalendarCreateInput

    def _run(self, *args, **kwargs):
        raise NotImplementedError("Use arun instead")

    async def _arun(self, user_email: str, calendar_id: str,
             event_name: str, start_datetime: str, end_datetime: str) -> dict:
        return await create_event(
            user_email,
            calendar_id,
            event_name,
            start_datetime,
            end_datetime
        )

class CalendarDeleteInput(BaseModel):
    """Input schema for DeleteCalendarEventTool."""
    user_email: str = Field(..., description="Email of the user")
    calendar_id: str = Field(..., description="Calendar ID")
    event_id: str = Field(..., description="Event ID to delete")

class DeleteCalendarEventTool(CalendarBaseTool):
    name: str = "delete_calendar_event"
    description: str = "Delete a calendar event"
    args_schema: Type[CalendarDeleteInput] = CalendarDeleteInput

    def _run(self, *args, **kwargs):
        raise NotImplementedError("Use arun instead")

    async def _arun(self, user_email: str, calendar_id: str, event_id: str) -> dict:
        return await delete_event(user_email, calendar_id, event_id)
