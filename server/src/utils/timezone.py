from datetime import datetime
from zoneinfo import ZoneInfo

DEFAULT_TIMEZONE = "Asia/Seoul"

def to_local(dt: datetime) -> datetime:
    """Convert UTC datetime to local (KST) time"""
    if dt.tzinfo is None:  # Naive datetime
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.astimezone(ZoneInfo(DEFAULT_TIMEZONE))

def to_utc(dt: datetime) -> datetime:
    """Convert local (KST) datetime to UTC"""
    if dt.tzinfo is None:  # Naive datetime
        dt = dt.replace(tzinfo=ZoneInfo(DEFAULT_TIMEZONE))
    return dt.astimezone(ZoneInfo("UTC"))

def format_local_time(dt: datetime) -> str:
    """Format datetime in local timezone for display"""
    local_time = to_local(dt)
    return local_time.strftime("%Y-%m-%d %I:%M %p")
