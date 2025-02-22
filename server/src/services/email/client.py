from typing import List
from langchain_core.documents import Document
import json
import os

async def create_prompt_email(emails_data: str, query: str) -> str:
    """
    Create a formatted prompt for an email QA chatbot.

    Args:
        emails_data (str): Formatted email data.
        query (str): The user's question.

    Returns:
        str: The complete prompt for the chatbot.
    """
    system_prompt = (
        "You are an e-mail QA chatbot.\n"
        "Use the following emails to answer the question at the end in Korean.\n"
        "If you don't know the answer based on the emails, just say 'I can't answer it based on the data.'.\n"
    )
    
    prompt = (
        f"<start_of_turn>user\n"
        f"{system_prompt}\n\n"
        f"Retrieved Emails:\n{emails_data}\n\n"
        f"Question: {query}\n\n"
        "Answer:<end_of_turn>\n"
        "<start_of_turn>model\n"
    )
    
    return prompt

async def format_emails(documents: List[Document]) -> str:
    """
    Format multiple email documents with their metadata.

    Args:
        documents (List[Document]): List of email documents.

    Returns:
        str: A formatted string containing email metadata and content.
    """
    formatted_emails = []
    for i, doc in enumerate(documents, 1):
        metadata = doc.metadata
        email_content = (
            f"Email #{i}:\n"
            f"From: {metadata.get('from', 'Unknown')}\n"
            f"To: {metadata.get('to', 'Unknown')}\n"
            f"CC: {metadata.get('cc', 'None')}\n"
            f"Date: {metadata.get('date', 'Unknown')}\n"
            f"Subject: {metadata.get('subject', 'No Subject')}\n\n"
            "Content:\n"
            f"{doc.page_content}\n"
            "-------------------"
        )
        formatted_emails.append(email_content)
    
    return "\n".join(formatted_emails)