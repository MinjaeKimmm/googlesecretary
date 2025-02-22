from fastapi import APIRouter, Depends, HTTPException
from src.models.user import User
from src.services.database.elastic import return_drive, get_es_client
from src.services.drive.client import format_drive, create_prompt_drive
from typing import Dict
from src.models.drive import ChatRequest, ChatResponse, SetupRequest
from src.agents.llm_agent import generate_response
from src.process.drive.preprocess import embed_drive

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message about calendar events."""

    vector_store = await return_drive()
    # do not use first top directory of request.directory
    request.directory = request.directory.split("/")[1]
    search_kwargs = {
        "k": 3,
        "filter": {
            "bool": {
                "must": [
                    {"term": {"metadata.user_id.keyword": request.user_email}},
                    {
                        "wildcard": {
                            "metadata.file_path.keyword": {
                                "value": f"*{request.directory}*",
                                "case_insensitive": True,
                            }
                        }
                    },
                ]
            }
        },
    }

    retrieved_documents = await vector_store.as_retriever(
        search_kwargs=search_kwargs
    ).ainvoke(request.user_message)

    print(retrieved_documents)
    
    response = ""

    if retrieved_documents:
        formatted_emails = await format_drive(retrieved_documents)
        prompt = await create_prompt_drive(formatted_emails, request.user_message)
        response = await generate_response(prompt)
    else:
        response = "No drive files found."

    return ChatResponse(answer=response)


@router.post("/setup")
async def setup_drive(request: SetupRequest):
    """embed drive files."""
    try:
        vector_store = await return_drive()
        await embed_drive(vector_store, request.user_email)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/remove_all")
async def remove_all():
    """Remove all emails."""
    try:
        (await get_es_client()).indices.delete(index="drive", ignore=[400, 404])
        (await get_es_client()).indices.create(index="drive", ignore=400)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
