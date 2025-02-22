from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os
from dotenv import load_dotenv
from pathlib import Path

# Get the absolute path to the .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

class Settings(BaseSettings):
    # MongoDB settings
    mongodb_uri: str = os.getenv('MONGODB_URI')
    mongodb_database: str = os.getenv('MONGODB_DATABASE')
    
    # Google OAuth settings
    google_client_id: str = os.getenv('GOOGLE_CLIENT_ID')
    google_client_secret: str = os.getenv('GOOGLE_CLIENT_SECRET')
    
    # OpenAI settings
    openai_api_key: str = os.getenv('OPENAI_API_KEY')
    openai_model: str = os.getenv('OPENAI_MODEL')
    
    # Application settings
    frontend_url: str = os.getenv('NEXTAUTH_URL', 'http://localhost:3000')

    class Config:
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()