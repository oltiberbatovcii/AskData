"""App settings, loaded from environment variables and the `.env` file."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/ folder. Resolving from this file (not the current directory) means paths
# work no matter where you start the app or the tests from.
BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """All configurable values in one place. Env vars override these defaults."""

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",  # unknown keys in .env are ignored instead of crashing the app
    )

    # --- Database ---
    db_path: Path = BACKEND_DIR / "data" / "chinook.sqlite"
    row_limit: int = 100
    query_timeout_seconds: float = 5.0

    # --- LLM ---
    llm_provider: Literal["ollama", "anthropic", "openai"] = "ollama"
    llm_model: str = "qwen2.5-coder:7b"
    ollama_url: str = "http://localhost:11434"

    # --- API ---
    frontend_origin: str = "http://localhost:5173"  # Vite dev server, allowed by CORS

    @field_validator("db_path")
    @classmethod
    def resolve_db_path(cls, value: Path) -> Path:
        """Treat a relative DB path as relative to backend/, not the current directory."""
        return value if value.is_absolute() else BACKEND_DIR / value


@lru_cache
def get_settings() -> Settings:
    """Return one shared Settings object (created once, then reused)."""
    return Settings()
