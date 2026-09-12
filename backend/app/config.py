from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_DIR / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str

    chat_model: str = "gpt-4o-mini"
    embed_model: str = "text-embedding-3-small"
    chunk_size: int = 1000
    chunk_overlap: int = 150

    chroma_dir: Path = DATA_DIR / "chroma"
    checkpoint_dir: Path = DATA_DIR / "checkpoints"
    upload_dir: Path = DATA_DIR / "uploads"

    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
