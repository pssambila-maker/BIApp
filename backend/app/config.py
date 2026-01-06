"""Application configuration management."""
from typing import Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

    def get_cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(",")]
        return self.cors_origins

    # Application
    app_name: str = "Tableau App"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server
    host: str = "127.0.0.1"
    port: int = 8000
    workers: int = 4

    # Database
    database_url: str = "postgresql+asyncpg://tableau_user:password@localhost/tableau_app"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 50

    # Security
    secret_key: str = "CHANGE_THIS_TO_A_RANDOM_SECRET_KEY_IN_PRODUCTION"
    algorithm: str = "HS256"
    access_token_expire_hours: int = 8

    # Encryption (for data source credentials)
    encryption_key: Optional[str] = None  # Fernet key

    # Query Cache
    query_cache_ttl: int = 900  # 15 minutes
    query_cache_max_size_mb: int = 100

    # CORS
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Rate Limiting
    rate_limit_per_minute: int = 100

    # File Storage
    upload_dir: str = "./data/uploads"
    cache_dir: str = "./data/cache"
    export_dir: str = "./data/exports"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/1"


# Global settings instance
settings = Settings()
