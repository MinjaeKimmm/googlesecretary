from pydantic import BaseModel

class ChatRequest(BaseModel):
    user_email: str
    user_message: str
    directory: str

class ChatResponse(BaseModel):
    answer: str

class SetupRequest(BaseModel):
    user_email: str