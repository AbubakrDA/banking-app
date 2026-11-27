from typing import List
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "BankingAIPlatform"
    ENVIRONMENT: str = Field(default="development", description="development | staging | production")
    DEBUG: bool = Field(default=True)
    API_V1_STR: str = "/api/v1"

    # Security & Tokens
    SECRET_KEY: str = Field(default="banking-ai-platform-dev-secret-key-change-in-production-min32chars")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_ISSUER: str = Field(default="banking-ai-platform-auth")
    JWT_AUDIENCE: str = Field(default="banking-ai-platform-api")
    KEYCLOAK_JWKS_URL: str | None = Field(default=None)
    ALLOW_DEV_STATIC_JWT_SECRET: bool = Field(
        default=True,
        description="Dev/test-only HS256 static secret toggle; forbidden in staging/production.",
    )

    # Tenant Scoping
    TENANT_HEADER_NAME: str = "X-Tenant-ID"
    DEFAULT_TENANT_ID: str = "tenant_enterprise_01"

    # Database (PostgreSQL with pgvector)
    POSTGRES_SERVER: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_DB: str = Field(default="banking_ai_db")
    DATABASE_URL: str | None = None

    # Redis Cache & Broker
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_URL: str | None = None

    # Object Storage (MinIO / S3)
    S3_ENDPOINT: str = Field(default="http://localhost:9000")
    S3_ACCESS_KEY: str = Field(default="minioadmin")
    S3_SECRET_KEY: str = Field(default="minioadmin")
    S3_BUCKET_NAME: str = Field(default="banking-ai-platform-storage")

    # Malware Scanning (ClamAV)
    CLAMAV_ENABLED: bool = Field(default=False)
    CLAMAV_HOST: str = Field(default="localhost")
    CLAMAV_PORT: int = Field(default=3310)
    CLAMAV_SOCKET: str | None = None

    # Banking Domain & AI Stub
    HIGH_RISK_TRANSFER_MINOR: int = Field(default=100_000)
    LLM_PROVIDER: str = Field(default="stub")

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    def get_redis_url(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.ENVIRONMENT in ("production", "staging"):
            if (
                self.SECRET_KEY == "banking-ai-platform-dev-secret-key-change-in-production-min32chars"
                or len(self.SECRET_KEY) < 32
            ):
                raise ValueError(
                    "Security Violation: SECRET_KEY must be overridden with a 32+ char secret in staging/production."
                )
            if self.ALLOW_DEV_STATIC_JWT_SECRET:
                raise ValueError(
                    "Security Violation: ALLOW_DEV_STATIC_JWT_SECRET must be False in staging/production."
                )
            if not self.KEYCLOAK_JWKS_URL:
                raise ValueError(
                    "Security Violation: KEYCLOAK_JWKS_URL must be configured in staging/production."
                )
        return self
        return self


settings = Settings()
