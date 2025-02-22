from datetime import datetime, timedelta
from typing import Optional, Type
from pydantic import BaseModel, Field
from zoneinfo import ZoneInfo

from .base import CalendarBaseTool
from src.utils.timezone import to_utc, to_local, DEFAULT_TIMEZONE

class TimeDeltaInput(BaseModel):
    """Input schema for TimeDeltaTool."""
    delta_days: Optional[int] = Field(None, description="Number of days to add")
    delta_hours: Optional[int] = Field(None, description="Number of hours to add")
    delta_minutes: Optional[int] = Field(None, description="Number of minutes to add")
    delta_seconds: Optional[int] = Field(None, description="Number of seconds to add")

class TimeDeltaTool(CalendarBaseTool):
    name: str = "get_future_time"
    description: str = "Calculate a future time based on a time delta (days, hours, minutes, seconds)"
    args_schema: Type[TimeDeltaInput] = TimeDeltaInput

    async def _arun(self, delta_days: int = 0, delta_hours: int = 0,
             delta_minutes: int = 0, delta_seconds: int = 0) -> str:
        # Start with current time in local timezone
        current_local = datetime.now(ZoneInfo(DEFAULT_TIMEZONE))
        future_local = current_local + timedelta(
            days=delta_days or 0,
            hours=delta_hours or 0,
            minutes=delta_minutes or 0,
            seconds=delta_seconds or 0
        )
        # Convert to UTC for API
        future_utc = to_utc(future_local)
        return future_utc.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

class CurrentTimeInput(BaseModel):
    """Empty input schema for CurrentTimeTool."""
    pass

class CurrentTimeTool(CalendarBaseTool):
    name: str = "get_current_time"
    description: str = "Get the current time in RFC3339 format"
    args_schema: Type[CurrentTimeInput] = CurrentTimeInput

    async def _arun(self) -> str:
        current_utc = datetime.now(ZoneInfo("UTC"))
        return current_utc.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

class SpecificTimeInput(BaseModel):
    """Input schema for SpecificTimeTool."""
    year: int = Field(..., description="Year of the event")
    month: int = Field(..., description="Month of the event (1-12)")
    day: int = Field(..., description="Day of the event (1-31)")
    hour: int = Field(..., description="Hour of the event (0-23)")
    minute: int = Field(..., description="Minute of the event (0-59)")

class SpecificTimeTool(CalendarBaseTool):
    name: str = "set_specific_time"
    description: str = "Convert specific date and time components to RFC3339 format"
    args_schema: Type[SpecificTimeInput] = SpecificTimeInput

    async def _arun(self, year: int, month: int, day: int, hour: int, minute: int) -> str:
        # Create time in local timezone (KST)
        local_time = datetime(year, month, day, hour, minute, tzinfo=ZoneInfo(DEFAULT_TIMEZONE))
        # Convert to UTC for API
        utc_time = to_utc(local_time)
        return utc_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
