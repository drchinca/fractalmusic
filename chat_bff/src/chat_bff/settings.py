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
    ollama_model: str = "qwen2.5:14b"

    # Pipeline knobs
    retrieval_k: int = 8
    # I-3 threshold. Calibrated on 40 hand-labeled (claim, snippet) pairs;
    # F1=0.857, P=0.818, R=0.900 at this value. See
    # tests/eval/calibration_results.md for the sweep + the polar-negation
    # failure mode (cosine can't distinguish "X is Y" from "X is NOT Y").
    fidelity_threshold: float = 0.79
    max_regenerations: int = 1
    request_timeout_s: float = 30.0

    # Embedding model id — must match what the index was built with.
    embed_model: str = "nomic-embed-text"
