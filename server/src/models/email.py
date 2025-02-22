from typing import Optional, Dict, List
from pydantic import BaseModel
from datetime import datetime

class ChatRequest(BaseModel):
    user_email: str
    user_message: str

class ChatResponse(BaseModel):
    answer: str

class GoogleCredential(BaseModel):
    credential: str

class EmailMetadata(BaseModel):
    subject: str
    sender: str
    to: str
    cc: Optional[str] = None
    received_time: datetime
    has_html: bool = False

class ForwardedEmail(BaseModel):
    original_from: str
    original_to: str
    original_cc: Optional[str] = None
    original_subject: str
    original_date: str
    original_body: str
    forwarded_by: Dict[str, str]

class EmailMessage(BaseModel):
    subject: str
    conversation_topic: str
    order_in_conversation: int
    sender_name: str
    to: str
    cc: Optional[str] = None
    received_time: str
    body: str
    has_html: bool = False
    attachment_files: List[str] = []
    inline_images: List[str] = []
    forwarded_info: Optional[ForwardedEmail] = None

class SetupRequest(BaseModel):
    user_email: str
    credential: str