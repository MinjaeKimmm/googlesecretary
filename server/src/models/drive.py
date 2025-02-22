from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class ChatRequest(BaseModel):
    user_email: str
    user_message: str
    directory: str

class ChatResponse(BaseModel):
    answer: str

class FolderRequest(BaseModel):
    credential: str
    folderId: str = 'root'

class ListFoldersRequest(BaseModel):
    credential: str
    parentId: Optional[str] = None

class SetupRequest(BaseModel):
    user_email: str
    credential: str
    folderId: str = 'root'

class GoogleCredential(BaseModel):
    """Model for Google OAuth credentials"""
    credential: str