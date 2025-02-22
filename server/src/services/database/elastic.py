from elasticsearch import AsyncElasticsearch
from langchain_openai import OpenAIEmbeddings
from src.config.settings import get_settings
from elasticsearch.exceptions import ConnectionError as ESConnectionError
from langchain_elasticsearch import AsyncElasticsearchStore



async def init_elastic():
    global es_client, email_vector_store, drive_vector_store
    openai_embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    )
    

    settings = get_settings()
    es_client = AsyncElasticsearch(
        [settings.elastic_url],
        basic_auth=(settings.elastic_username, settings.elastic_password),
        verify_certs=False,
        request_timeout=10,
        retry_on_timeout=True
    )
        
    # Test connection
    if not await es_client.ping():
        raise ESConnectionError("Could not connect to Elasticsearch")
    
    email_vector_store = AsyncElasticsearchStore(
        es_connection=es_client,
        index_name="email",
        embedding=openai_embeddings
    )
    
    drive_vector_store = AsyncElasticsearchStore(
        es_connection=es_client,
        index_name="drive",
        embedding=openai_embeddings
    )
    es_client.indices.create(index="drive", ignore=400)
    es_client.indices.create(index="email", ignore=400)
    
    
async def return_email():
    return email_vector_store
    
async def return_drive():
    return drive_vector_store

async def get_es_client():
    return es_client