"""Tests for the ingest settings (S003A)."""

from __future__ import annotations

from nfl.config import Settings


def test_default_seasons_spans_the_history_window() -> None:
    s = Settings(history_start_season=2022, default_season=2025)

    assert s.default_seasons == [2022, 2023, 2024, 2025]


def test_default_seasons_is_inclusive_of_both_ends() -> None:
    s = Settings(history_start_season=2024, default_season=2024)

    assert s.default_seasons == [2024]


def test_history_window_widens_from_config_alone() -> None:
    """Adding history is an env var, not a code change."""
    s = Settings(history_start_season=2016, default_season=2025)

    assert len(s.default_seasons) == 10
    assert s.default_seasons[0] == 2016
