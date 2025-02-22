from typing import List
from langchain_core.documents import Document


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
