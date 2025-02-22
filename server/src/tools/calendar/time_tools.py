from datetime import datetime, timedelta
from typing import Optional, Type
from pydantic import BaseModel, Field
from zoneinfo import ZoneInfo

from .base import CalendarBaseTool

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
        future_time = datetime.utcnow() + timedelta(
            days=delta_days or 0,
            hours=delta_hours or 0,
            minutes=delta_minutes or 0,
            seconds=delta_seconds or 0
        )
        return future_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

class CurrentTimeInput(BaseModel):
    """Empty input schema for CurrentTimeTool."""
    pass

class CurrentTimeTool(CalendarBaseTool):
    name: str = "get_current_time"
    description: str = "Get the current time in RFC3339 format"
    args_schema: Type[CurrentTimeInput] = CurrentTimeInput

    async def _arun(self) -> str:
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")

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
        # Create time in Asia/Seoul timezone
        local_tz = ZoneInfo("Asia/Seoul")
        specific_time = datetime(year, month, day, hour, minute, tzinfo=local_tz)
        # Convert to UTC
        utc_time = specific_time.astimezone(ZoneInfo("UTC"))
        return utc_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
