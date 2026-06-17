from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Candidate Service"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

settings = Settings()