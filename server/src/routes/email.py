from fastapi import APIRouter, Depends, HTTPException
from src.models.user import User
from src.services.database.elastic import return_drive, return_email, get_es_client
from src.services.email.client import format_emails, create_prompt_email
from typing import Dict
from src.models.email import ChatRequest, ChatResponse, SetupRequest
from src.agents.llm_agent import generate_response
from src.process.email.preprocess import embed_email


router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message about calendar events."""
    try:
        vector_store = await return_email()
        # TODO: Implement a search query to retrieve relevant emails
        search_kwargs = {
            "k": 3,
            "filter": {"term": {"metadata.user_id.keyword": request.user_email}},
        }

        retrieved_documents = await vector_store.as_retriever(
            search_kwargs=search_kwargs
        ).ainvoke(request.user_message)
        
        response = ""
        
        if retrieved_documents:
            formatted_emails = await format_emails(retrieved_documents)
            prompt = await create_prompt_email(formatted_emails, request.user_message)
            response = await generate_response(prompt)
        else:
            response = "No emails found."
            
        return ChatResponse(answer=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/setup")
async def setup_email(request: SetupRequest):
    """embed emails."""
    try:
        vector_store = await return_email()
        await embed_email(vector_store,request.user_email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/remove_all")
async def remove_all():
    """Remove all emails."""
    try:
        (await get_es_client()).indices.delete(index="email", ignore=[400, 404])
        (await get_es_client()).indices.create(index="email", ignore=400)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))