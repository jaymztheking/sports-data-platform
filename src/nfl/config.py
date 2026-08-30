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
    # NFL_HISTORY_START_SEASON — earliest season ingested. One season cannot separate
    # a genuine level shift from an outlier year, and per-game rates off a short
    # injury-hit season are noisy, so the draft board is built on a window. Widening
    # the history is this one env var, not a code change.
    history_start_season: int = Field(default=2022)
    # NFL_DEFAULT_SEASON — most recent complete season; the top of the window.
    default_season: int = Field(default=2025)
    # NFL_CURRENT_SEASON — the upcoming season. Distinct from `default_season`: role/board
    # data (depth charts, live ADP) describes the season ahead, which has no played games
    # to summarize yet, so it can't live in the historical window.
    current_season: int = Field(default=2026)

    @property
    def default_seasons(self) -> list[int]:
        """Every season in the history window, oldest first."""
        return list(range(self.history_start_season, self.default_season + 1))


settings = Settings()
