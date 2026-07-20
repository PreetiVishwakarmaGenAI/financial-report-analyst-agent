from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration."""

    # Anthropic
    ANTHROPIC_API_KEY: str
    MODEL_NAME: str = "claude-sonnet-4"

    # LangSmith
    LANGCHAIN_API_KEY: str
    LANGCHAIN_TRACING_V2: bool = True
    LANGCHAIN_PROJECT: str = "financial-analyst-agent"

    # Embeddings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # RAG
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    VECTOR_DB_PATH: str = "./data/chroma_db"
    VECTOR_COLLECTION_NAME: str = "financial_reports"

    # Authentication
    JWT_SECRET_KEY: str

    # FastAPI
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
