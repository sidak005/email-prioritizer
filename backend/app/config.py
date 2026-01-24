from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Supabase
    supabase_url: str
    supabase_key: str
    
    # Pinecone
    pinecone_api_key: str
    pinecone_environment: str
    pinecone_index_name: str = "email-prioritizer"
    
    # Hugging Face
    huggingface_api_key: str
    
    # Gmail (Optional)
    gmail_client_id: Optional[str] = None
    gmail_client_secret: Optional[str] = None
    gmail_refresh_token: Optional[str] = None
    
    # App
    environment: str = "development"
    api_key: Optional[str] = None
    log_level: str = "INFO"
    
    # Redis (Optional)
    redis_url: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
