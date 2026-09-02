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

    # Where the JSON pattern corpus lives (BE-only; FE never touches it).
    # Absolute default keeps the corpus consistent regardless of CWD.
    corpus_root: Path = Field(
        default=Path(__file__).resolve().parent.parent.parent.parent / "patterns",
    )

    # Where rendered WAVs are written. Vite serves web/public/* at /,
    # so a file at web/public/generated/<hash>.wav reaches the FE as
    # /generated/<hash>.wav. Default points at the repo's web/public.
    audio_cache_dir: Path = Field(
        default=Path(__file__).resolve().parent.parent.parent.parent / "web" / "public" / "generated",
    )
    # URL prefix the FE uses to fetch from the cache_dir.
    audio_cache_url: str = "/generated"
    # Optional SoundFont. Render uses pyfluidsynth if both this file and the
    # python package are present; otherwise falls back to numpy synth.
    soundfont_path: Path | None = None
    # Optional impulse response. If absent, an algorithmic hall is used.
    reverb_ir_path: Path | None = None

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
