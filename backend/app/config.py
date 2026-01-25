from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Supabase
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    
    # Pinecone
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    pinecone_index_name: str = "email-prioritizer"
    
    # Hugging Face
    huggingface_api_key: Optional[str] = None
    
    # gmail_client_id: Optional[str] = None
    # gmail_client_secret: Optional[str] = None
    # gmail_refresh_token: Optional[str] = None
    
    # App
    environment: str = "development"
    api_key: Optional[str] = None
    log_level: str = "INFO"
    
    # redis_url: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env that aren't in Settings

settings = Settings()
