from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # App
    APP_NAME: str = "Parkash Book Depot API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str = Field(...)
    PEPPER: str = Field(...)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 3

    # MongoDB
    MONGODB_URL: str = Field(...)
    MONGODB_DB_NAME: str = "parkash_book_depot"

    # CORS
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:5173", "http://localhost:3000"]
    )

    # Request limits
    MAX_REQUEST_SIZE_MB: int = 5

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: str = Field(...)
    CLOUDINARY_API_KEY: str = Field(...)
    CLOUDINARY_API_SECRET: str = Field(...)

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_be_strong(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters. "
                "Generate with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        return v

    @field_validator("PEPPER")
    @classmethod
    def pepper_must_be_strong(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError(
                "PEPPER must be at least 32 characters. "
                "Generate with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        return v


settings = Settings()