from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Intelligence Service"

    MODEL_NAME: str = "command-a-03-2025"
    COHERE_API_KEY: str
    FALLBACK_MODEL_NAME: str = "llama-3.3-70b-versatile"
    GROQ_API_KEY: str
    
    TEMPERATURE: float = 0.0
    MAX_TOKENS: int = 1000
    LLM_TIMEOUT: float = 15.0

    QDRANT_URL: str
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "candidates"
    
    SEARCH_API_URL: str
    CANDIDATE_SERVICE_INTERNAL_URL: str

settings = Settings()