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

    # App
    environment: str = "development"
    api_key: Optional[str] = None
    log_level: str = "INFO"
    use_llm_priority: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

settings = Settings()
