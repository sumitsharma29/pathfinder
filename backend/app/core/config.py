import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "PathFinder AI"
    APP_ENV: str = "development"
    APP_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/pathfinder"
    
    # Security
    SECRET_KEY: str = "pathfinder_local_development_secret_key_2026_super_secure"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:5173,http://localhost:3000"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:5173"]

    # AI & Embeddings
    EMBEDDING_DIMENSION: int = 1536
    EMBEDDING_PROVIDER: str = "mock"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_API_KEY: str = ""
    
    LLM_PROVIDER: str = "mock"
    LLM_MODEL: str = "gemini-1.5-flash"
    LLM_API_KEY: str = ""
    
    AI_TIMEOUT_SECONDS: int = 30
    AI_MAX_RETRIES: int = 2
    AI_MAX_TOKENS: int = 2000
    AI_TEMPERATURE: float = 0.2
    
    RAG_TOP_K: int = 5
    RAG_SIMILARITY_THRESHOLD: float = 0.50
    RATE_LIMIT_ENABLED: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Security & Request Limits (SECURITY_SPEC.md §49, §52)
    MAX_REQUEST_BODY_BYTES: int = 2 * 1024 * 1024  # 2MB
    RATE_LIMIT_AI_PER_MINUTE: int = 30
    RATE_LIMIT_AUTH_PER_MINUTE: int = 10
    RATE_LIMIT_ROADMAP_PER_MINUTE: int = 15
    
    # Recommendation Scoring Weights (must sum to 1.0)
    SKILL_GAP_WEIGHT: float = 0.30
    PREREQUISITE_WEIGHT: float = 0.20
    GOAL_WEIGHT: float = 0.15
    DIFFICULTY_WEIGHT: float = 0.15
    TIME_WEIGHT: float = 0.10
    PREFERENCE_WEIGHT: float = 0.10
    
    # Adaptive Learning & Mastery Thresholds (AI_SPEC.md §31, TECHNICAL.md §50)
    MASTERY_MASTERED: float = 80.0
    MASTERY_CONTINUE: float = 60.0
    MASTERY_REINFORCEMENT: float = 40.0

    model_config = SettingsConfigDict(
        env_file=[
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.env")),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env")),
            ".env"
        ],
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
