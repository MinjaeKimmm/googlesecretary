import fal_client
from fastapi import APIRouter, Depends, HTTPException
from src.models.user import User
from src.services.database.elastic import return_drive, get_es_client
from src.services.drive.client import format_drive, create_prompt_drive
from typing import Dict
from src.models.drive import ChatRequest, ChatResponse, SetupRequest
from src.agents.llm_agent import generate_response
from src.process.drive.preprocess import embed_drive
from fastapi.responses import StreamingResponse

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest):
    """Process a chat message about calendar events."""

    vector_store = await return_drive()
    # do not use first top directory of request.directory
    request.directory = "/".join(request.directory.split("/")[1:])
    print(request.directory)
    search_kwargs = {
        "k": 10,
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

    formatted_emails = await format_drive(retrieved_documents)
    prompt = await create_prompt_drive(formatted_emails, request.user_message)

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
        es_client = await get_es_client()
        # Delete the "drive" index; ignore errors if it doesn't exist.
        await es_client.indices.delete(index="drive", ignore=[400, 404])
        # Re-create the "drive" index.
        await es_client.indices.create(index="drive", ignore=400)
        return {"detail": "All drive files have been removed."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get_all")
async def get_all():
    """Get all drive."""
    try:
        res = await (await get_es_client()).search(
            index="drive", body={"query": {"match_all": {}}}
        )
        # print results one by one
        for hit in res["hits"]["hits"]:
            print(hit["_source"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
