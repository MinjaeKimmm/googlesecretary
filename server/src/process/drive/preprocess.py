
from typing import *
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bs4 import BeautifulSoup
from langchain_elasticsearch import AsyncElasticsearchStore, ElasticsearchStore
from elasticsearch import Elasticsearch
from dataclasses import dataclass
from elasticsearch.exceptions import ConnectionError as ESConnectionError
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.llms.vllm import VLLM
from langchain_core.documents import Document
import json
import os
from markitdown import MarkItDown
import uvicorn



def embed_drive(root, vector_store, user_id):
    list_all_files = []
    for r, dirs, files in os.walk(root):
        for file in files:
            list_all_files.append(os.path.join(r, file))
    md = MarkItDown(enable_plugins=False)
    for file in list_all_files:
        metadata = {
            "user_id": user_id,
            "file_path": file,
            "file_name": os.path.basename(file),
            "file_type": os.path.splitext(file)[1],
            "data_source": "drive",
        }
        res = md.convert(os.path.join(root, file))
        if not res.text_content or res.text_content == "" or res.text_content is None:
            print("No content in file")
        else:
            document = Document(page_content=res.text_content, metadata=metadata)
            uuid = str(uuid4())
            vector_store.add_documents(documents=[document], ids=[uuid])
            
            
async def embed_drive(vector_store:AsyncElasticsearchStore,  user_id:str):
    try:
        root = os.path.join(os.environ["ROOT_LOCATION"], "data", user_id, "drive")
        list_all_files = []
        for r, dirs, files in os.walk(root):
            for file in files:
                list_all_files.append(os.path.join(r, file))
        md = MarkItDown(enable_plugins=False)
        for file in list_all_files:
            metadata = {
                "user_id": user_id,
                "file_path": file,
                "file_name": os.path.basename(file),
                "file_type": os.path.splitext(file)[1],
                "data_source": "drive",
            }
            if os.path.splitext(file)[1] not in [".pdf", ".docx", ".txt",".xls",".xlsx",".ppt",".pptx"]:
                print("File type not supported for file{}".format(file))
                continue
            res = md.convert(os.path.join(root, file))
            if not res.text_content or res.text_content == "" or res.text_content is None:
                print("No content in file")
            else:
                document = Document(page_content=res.text_content, metadata=metadata)
                uuid = str(uuid4())
                await vector_store.aadd_documents(documents=[document], ids=[uuid])

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))