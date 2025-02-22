import fal_client
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from src.models.drive import ChatRequest, ChatResponse, GoogleCredential
from src.services.database.elastic import return_drive, get_es_client
from src.services.database.mongodb import get_db
from src.services.drive.client import format_drive, create_prompt_drive, get_drive_service
from src.services.drive.storage import DriveStorage
from src.services.drive.parser import parse_folder_contents, format_folder_structure
from src.agents.llm_agent import generate_response
from src.process.drive.preprocess import embed_drive
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

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


class DriveSetupRequest(BaseModel):
    credential: GoogleCredential
    user_email: str
    folderId: str

@router.post("/setup")
async def setup_drive(
    request: DriveSetupRequest,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """Setup drive service for a user."""
    try:
        print(f"Starting Drive setup for user: {request.user_email}")
        
        # Initialize Drive service
        print("Initializing Drive service")
        service = get_drive_service(request.credential.token)
        storage = DriveStorage(request.user_email)
        
        # Check if folder exists and needs update
        print("Checking folder status")
        folder_contents = parse_folder_contents(service, request.folderId, depth=2)
        print(f"Found {len(folder_contents)} items in folder")
        
        folder_data = {
            'id': request.folderId,
            'name': request.folderId,
            'contents': folder_contents
        }
        
        if await storage.should_update(request.folderId):
            print("Updating existing folder backup")
            await storage.update_folder(
                service,
                folder_id=request.folderId,
                topic=request.folderId,
                metadata=folder_data,
                content=format_folder_structure(folder_contents)
            )
            print("Folder update completed")
        else:
            print("Creating new folder backup")
            await storage.backup_folder(
                folder_id=request.folderId,
                topic=request.folderId,
                metadata=folder_data,
                content=format_folder_structure(folder_contents)
            )
            print("Folder backup completed")

        # Embed in vectorstore
        """
        try:
            print("Starting vector store embedding")
            vector_store = await return_drive()
            await embed_drive(vector_store, request.user_email)
            print("Vector store embedding completed")
        except Exception as e:
            print(f"Vector store operation failed: {str(e)}")
            raise
        """

        # Update database
        """
        print("Updating user service status in database")
        await db.users.update_one(
            {"email": request.user_email},
            {
                "$set": {
                    "services.drive.is_setup": True,
                    "services.drive.last_setup_time": datetime.utcnow(),
                    "services.drive.scope_version": "v1",
                    "google_credentials": request.credential.dict()
                }
            }
        )
        print("Database update completed")
        """
        print(f"Drive setup completed successfully for user: {request.user_email}")
        return {"status": "success", "path": str(storage.drive_path)}
    except Exception as e:
        print(f"Drive setup failed for user {request.user_email}: {str(e)}")
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
