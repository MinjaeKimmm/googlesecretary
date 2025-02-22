# Google API endpoints
GOOGLE_OAUTH_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# Google Calendar API
CALENDAR_API_BASE = "https://www.googleapis.com/calendar/v3"
CALENDAR_LIST_URL = f"{CALENDAR_API_BASE}/users/me/calendarList"
CALENDAR_EVENTS_URL = f"{CALENDAR_API_BASE}/calendars"

# Gmail API
GMAIL_API_BASE = "https://www.googleapis.com/gmail/v1/users/me"
GMAIL_MESSAGES_URL = f"{GMAIL_API_BASE}/messages"
GMAIL_LABELS_URL = f"{GMAIL_API_BASE}/labels"

# Google Drive API
DRIVE_API_BASE = "https://www.googleapis.com/drive/v3"
DRIVE_FILES_URL = f"{DRIVE_API_BASE}/files"
DRIVE_FOLDERS_URL = f"{DRIVE_API_BASE}/folders"

# OAuth scopes
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/drive.file",
    "openid",
    "email",
    "profile"
]
