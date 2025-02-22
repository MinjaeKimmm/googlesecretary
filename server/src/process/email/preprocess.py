from datetime import datetime
from typing import *
from uuid import uuid4
from fastapi import HTTPException
from langchain_core.documents import Document
import json
import os
from markitdown import MarkItDown
from langchain_elasticsearch import AsyncElasticsearchStore

async def embed_email(vector_store:AsyncElasticsearchStore,  user_id:str):
    try:
        root_attachment_file_loc = os.path.join(os.environ["ROOT_LOCATION"], "data", user_id)
        json_loc = os.path.join(os.environ["ROOT_LOCATION"], "data", user_id, "emails", "email_conversations.json")
        
        md = MarkItDown(enable_plugins=False)
        with open(json_loc, "r", encoding='UTF8') as f:
            data = json.load(f)

        for email in data:
            conversation_id = email.get("ConversationID")
            topic = email.get("Topic")
            for message in email.get("Messages"):
                received_time = message.get("ReceivedTime")
                # remove whatever is in the brackets
                received_time = received_time[0:10] + received_time[15:]
                parsed_date = (
                    datetime.strptime(received_time, "%Y-%m-%d %H:%M:%S (UTC%z)")
                    if received_time
                    else None
                )
                metadata = {
                    "from": message.get("SenderName"),
                    "to": message.get("To"),
                    "cc": message.get("CC"),
                    "date": message.get("ReceivedTime"),
                    "subject": message.get("Subject"),
                    "year": parsed_date.year if parsed_date else None,
                    "month": parsed_date.month if parsed_date else None,
                    "day": parsed_date.day if parsed_date else None,
                    "time": parsed_date.strftime("%H:%M:%S") if parsed_date else None,
                    "forwarded_by": message.get("ForwardedBy", {}).get("From"),
                    "conversation_id": conversation_id,
                    "topic": topic,
                    "user_id": user_id,
                    "data_source": "email",
                }

                attach_paths = message.get("AttachmentFiles")
                if attach_paths and len(attach_paths) > 0:
                    for attach_path in attach_paths:

                        if not os.path.exists(os.path.join(root_attachment_file_loc, attach_path)):
                            raise ValueError(
                                f"Attachment file not found: {attach_path}"
                            )
                        if os.path.splitext(attach_path)[1] not in [".pdf", ".docx", ".txt",".xls",".xlsx",".ppt",".pptx"]:
                            print("File type not supported for file{}".format(attach_path))
                            continue
                        res = md.convert(os.path.join(root_attachment_file_loc, attach_path))
                        # print(res.text_content)
                        if (
                            not res.text_content
                            or res.text_content == ""
                            or res.text_content is None
                        ):
                            print("No body content found in email")
                        else:
                            # saving attachment content
                            document = Document(
                                page_content=res.text_content, metadata=metadata
                            )
                            uuid = str(uuid4())
                            print
                            await vector_store.aadd_documents(documents=[document], ids=[uuid])

                body_content = message.get("Body")
                document = Document(page_content=body_content, metadata=metadata)
                uuid = str(uuid4())
                await vector_store.aadd_documents(documents=[document], ids=[uuid])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
