"""Env-loaded settings. Frozen. Validated at process start, never per request."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ChatSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CHAT_BFF_",
        env_file=".env",
        env_file_encoding="utf-8",
        frozen=True,
        extra="ignore",
    )

    # Where the meridian-built index lives. Default matches the existing
    # ~/.meridian/library install used by the CLI.
    index_dir: Path = Field(default=Path.home() / ".meridian" / "library")

    # LLM settings
    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-4-6"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    # Pipeline knobs
    retrieval_k: int = 8
    fidelity_threshold: float = 0.55  # I-3 threshold; PROVISIONAL until calibrated
    max_regenerations: int = 1
    request_timeout_s: float = 30.0

    # Embedding model id — must match what the index was built with.
    embed_model: str = "nomic-embed-text"
