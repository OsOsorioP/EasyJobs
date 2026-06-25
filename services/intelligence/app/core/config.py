from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Intelligence Service"

    MODEL_NAME: str = "command-a-03-2025"
    COHERE_API_KEY: str
    COHERE_EMBED_MODEL: str = "embed-multilingual-v3.0"
    FALLBACK_MODEL_NAME: str = "llama-3.3-70b-versatile"
    GROQ_API_KEY: str

    TEMPERATURE: float = 0.0
    MAX_TOKENS: int = 1500
    MAX_TOKENS_COMPARISON: int = 3000
    LLM_TIMEOUT: float = 50.0

    QDRANT_URL: str
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "candidates"

    CANDIDATE_SERVICE_INTERNAL_URL: str
    INTERNAL_SERVICE_TOKEN: Optional[str] = None

    CSV_BATCH_SIZE: int = 50
    PDF_BATCH_SIZE: int = 20

    @field_validator("LLM_TIMEOUT")
    @classmethod
    def timeout_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("LLM_TIMEOUT must be positive")
        return v

settings = Settings()