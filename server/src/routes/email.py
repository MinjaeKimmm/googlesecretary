import fal_client
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from src.models.user import User
from src.services.database.elastic import return_drive, return_email, get_es_client
from src.services.email.client import format_emails, create_prompt_email
from typing import Dict
from src.models.email import ChatRequest, ChatResponse, SetupRequest
from src.agents.llm_agent import generate_response
from src.process.email.preprocess import embed_email


router = APIRouter()

@router.post("/chat")
async def chat(request: ChatRequest):
    """Process a chat message about calendar events."""
    try:
        vector_store = await return_email()
        # TODO: Implement a search query to retrieve relevant emails
        search_kwargs = {
            "k": 10,
            "filter": {"term": {"metadata.user_id.keyword": request.user_email}},
        }

        retrieved_documents = await vector_store.as_retriever(
            search_kwargs=search_kwargs
        ).ainvoke(request.user_message)
        
        response = ""
        
        if retrieved_documents:
            formatted_emails = await format_emails(retrieved_documents)
            prompt = await create_prompt_email(formatted_emails, request.user_message)
        
        async def event_generator(prompt):
            # Initiate the async stream call with the prompt argument.
            stream_obj = fal_client.stream_async(
                "fal-ai/any-llm",
                arguments={
                    "prompt": prompt,
                    "model": "anthropic/claude-3.5-sonnet",
                },
            )
            # Iterate over the stream and yield each event formatted as an SSE message.
            async for event in stream_obj:
                # SSE requires messages to be prefixed with "data:" and separated by a double newline.
                yield f"data: {event}\n\n"

        # Return a StreamingResponse with the event_generator and set the media type accordingly.
        return StreamingResponse(event_generator(prompt), media_type="text/event-stream")
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
        es_client = await get_es_client()
        # Delete the "drive" index; ignore errors if it doesn't exist.
        await es_client.indices.delete(index="email", ignore=[400, 404])
        # Re-create the "drive" index.
        await es_client.indices.create(index="email", ignore=400)
        return {"detail": "All email files have been removed."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/get_all")
async def get_all():
    """Get all emails."""
    try:
        res = await ((await get_es_client()).search(
            index="email", body={"query": {"match_all": {}}}
        ))
        # print results one by one
        for hit in res["hits"]["hits"]:
            print(hit["_source"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))