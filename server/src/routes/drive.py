from fastapi import APIRouter, Depends, HTTPException
from src.models.user import User
from src.services.database.elastic import return_drive
from src.services.drive.client import format_drive, create_prompt_drive
from typing import Dict
from src.models.drive import ChatRequest, ChatResponse, SetupRequest
from src.agents.llm_agent import generate_response
from src.data.drive.preprocess import embed_drive

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message about calendar events."""
    try:
        vector_store = await return_drive()
        # TODO: Implement a search query to retrieve relevant drive
        search_kwargs = {
            "k": 3,
            "filter": {"term": {"metadata.user_id.keyword": request.user_email}},
        }

        retrieved_documents = await vector_store.as_retriever(
            search_kwargs=search_kwargs
        ).ainvoke(request.user_message)
        
        response = ""
        
        if retrieved_documents:
            formatted_emails = await format_drive(retrieved_documents)
            prompt = await create_prompt_drive(formatted_emails, request.user_message)
            response = await generate_response(prompt)
        else:
            response = "No drive files found."
            
        return ChatResponse(answer=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/setup")
async def setup_drive(request: SetupRequest):
    """embed drive files."""
    try:
        vector_store = await return_drive()
        await embed_drive(request.root, vector_store, request.user_email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        