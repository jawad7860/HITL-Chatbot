"""Application settings, loaded from environment variables / .env file."""
from functools import lru_cache
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    # LLM
    groq_api_key: str = Field(..., description="Groq API key")
    llm_model: str = Field(default="llama-3.3-70b-versatile")
    # Tools
    github_token: str = Field(default="", description="Optional GitHub token")
    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    # CORS
    cors_origins: str = Field(default="http://localhost:3000")
    # Checkpoint storage
    checkpoint_db: str = Field(default="data/checkpoints.db")
    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
