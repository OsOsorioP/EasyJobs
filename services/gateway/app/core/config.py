from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "API Gateway"

    IDENTITY_SERVICE_URL: str
    CANDIDATE_SERVICE_URL: str
    INTELLIGENCE_SERVICE_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str

    ALLOW_ORGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5001",
    ]

    PUBLIC_PATHS: tuple[str, ...] = (
        "/identity/api/v1/auth/register",
        "/identity/api/v1/auth/login",
        "/identity/api/v1/auth/refresh",
    )

settings = Settings()