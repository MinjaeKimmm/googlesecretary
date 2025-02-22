from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_email: str
    user_message: str

class ChatResponse(BaseModel):
    answer: str

class SetupRequest(BaseModel):
    root : str
    user_email: str