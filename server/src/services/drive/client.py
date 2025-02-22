from typing import List, Dict
from langchain_core.documents import Document
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive.metadata.readonly'
]

def get_drive_service(token: str):
    """Create and return a Drive service instance."""
    try:
        print("Creating Drive service with provided token")
        credentials = Credentials(
            token=token,
            scopes=SCOPES
        )
        service = build('drive', 'v3', credentials=credentials)
        print("Drive service created successfully")
        return service
    except HttpError as e:
        print(f"Google API error creating Drive service: {str(e)}")
        raise
    except Exception as e:
        print(f"Unexpected error creating Drive service: {str(e)}")
        raise

def get_folder_path(service, folder_id: str, path_segments: list = None) -> list:
    """Get the complete path to a folder from root."""
    if path_segments is None:
        path_segments = []
    
    try:
        folder = service.files().get(
            fileId=folder_id,
            fields='name, parents'
        ).execute()
        
        from ...utils.files import create_safe_name
        path_segments.insert(0, create_safe_name(folder.get('name', folder_id)))
        
        # Get parent folder if it exists
        parents = folder.get('parents', [])
        if parents and parents[0] != 'root':
            return get_folder_path(service, parents[0], path_segments)
        
        return path_segments
    except Exception as e:
        print(f"Error getting folder path: {str(e)}")
        return path_segments

async def list_folders(service, parent_id: str = None) -> Dict:
    """List folders in Drive."""
    try:
        results = []
        
        # Build query
        if parent_id is None:
            query = "trashed=false and mimeType='application/vnd.google-apps.folder' and 'root' in parents"
        else:
            query = f"trashed=false and mimeType='application/vnd.google-apps.folder' and '{parent_id}' in parents"
        
        response = service.files().list(
            q=query,
            spaces='drive',
            fields='files(id, name, mimeType)'
        ).execute()
        
        folders = response.get('files', [])
        
        for folder in folders:
            try:
                # Check for children
                children_response = service.files().list(
                    q=f"trashed=false and mimeType='application/vnd.google-apps.folder' and '{folder['id']}' in parents",
                    spaces='drive',
                    pageSize=1,
                    fields='files(id)'
                ).execute()
                
                has_children = len(children_response.get('files', [])) > 0
                
                results.append({
                    'id': folder['id'],
                    'name': folder['name'],
                    'path': folder['name'],
                    'mimeType': folder['mimeType'],
                    'parentId': parent_id,
                    'hasChildren': has_children
                })
            except Exception as folder_error:
                print(f"Error processing folder {folder.get('name', 'unknown')}: {str(folder_error)}")
                continue
        
        return {"folders": results}
        
    except Exception as e:
        print(f"Error listing folders: {str(e)}")
        raise


async def format_drive(documents: List[Document]) -> str:
    """
    Format multiple drive documents with their metadata.

    Args:
        documents (List[Document]): List of drive documents.

    Returns:
        str: A formatted string containing drive metadata and content.
    """
    formatted_drive = []
    for i, doc in enumerate(documents, 1):
        metadata = doc.metadata
        drive_content = (
            f"Drive File #{i}:\n"
            f"File Name: {metadata.get('file_name', 'Unknown')}\n"
            f"File Type: {metadata.get('file_type', 'Unknown')}\n"
            f"File Path: {metadata.get('file_path', 'Unknown')}\n\n"
            "Content:\n"
            f"{doc.page_content}\n"
            "-------------------"
        )
        formatted_drive.append(drive_content)
    
    return "\n".join(formatted_drive)
            
            
async def create_prompt_drive(drive_data: str, query: str) -> str:
    """
    Create a formatted prompt for a drive QA chatbot.

    Args:
        drive_data (str): Formatted drive data.
        query (str): The user's question.

    Returns:
        str: The complete prompt for the chatbot.
    """
    system_prompt = (
        "You are a Google Drive QA chatbot.\n"
        "Use the following drive files to answer the question at the end in the language of the question.\n"
        "If you don't know the answer based on the drive files, respond with 'I can't answer it based on the data.'.\n"
    )
    
    prompt = (
        f"<start_of_turn>user\n"
        f"{system_prompt}\n\n"
        f"Retrieved Drive Files:\n{drive_data}\n\n"
        f"Question: {query}\n\n"
        "Answer:<end_of_turn>\n"
        "<start_of_turn>model\n"
    )
    
    return prompt
