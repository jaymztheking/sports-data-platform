"""Runtime configuration for NFL ingestion.

Reference implementation (S003 scaffold). Values load from the environment with
the ``NFL_`` prefix (and an optional ``.env``); see ``.env.example``.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Paths and defaults shared by the ingestion modules."""

    model_config = SettingsConfigDict(
        env_prefix="NFL_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # NFL_DATA_DIR — where ingest reads/writes Parquet. Dev points at data/raw;
    # CI overrides it to data/samples (the committed no-network slice).
    data_dir: Path = Field(default=Path("data/raw"))
    # NFL_DEFAULT_SEASON — season used when --season is omitted.
    default_season: int = Field(default=2025)


settings = Settings()
