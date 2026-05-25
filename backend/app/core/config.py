from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List


def parse_allowed_origins(value: str | List[str] | None) -> List[str]:
    """Parse ALLOWED_ORIGINS from string or list."""
    
    if value is None:
        return [
            "http://localhost:5173",
            "http://localhost:3000",
            "https://parkash-book-depot.vercel.app",
            "https://parkash-book-depot-nxr52hx3l-dron-gargs-projects.vercel.app",
        ]

    if isinstance(value, list):
        return value

    if isinstance(value, str):
        return [o.strip() for o in value.split(",") if o.strip()]

    return [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://parkash-book-depot.vercel.app",
        "https://parkash-book-depot-nxr52hx3l-dron-gargs-projects.vercel.app",
    ]


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

    # API
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str = Field(
        ...,
        description="JWT secret key — must be strong and random in production"
    )

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 3

    # MongoDB
    MONGODB_URL: str = Field(
        ...,
        description="MongoDB connection URL"
    )

    MONGODB_DB_NAME: str = "parkash_book_depot"

    # CORS
    ALLOWED_ORIGINS_STR: str = Field(
        default=(
            "http://localhost:5173,"
            "http://localhost:3000,"
            "https://parkash-book-depot.vercel.app,"
            "https://parkash-book-depot-nxr52hx3l-dron-gargs-projects.vercel.app"
        ),
        alias="ALLOWED_ORIGINS"
    )

    @property
    def allowed_origins(self) -> List[str]:
        """Get parsed ALLOWED_ORIGINS list."""
        return parse_allowed_origins(self.ALLOWED_ORIGINS_STR)


# Single shared instance
settings = Settings()