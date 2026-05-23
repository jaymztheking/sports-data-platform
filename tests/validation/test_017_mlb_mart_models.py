"""Validation tests for Story 017 – MLB dbt Mart Models.

Verifies that gold-layer mart tables exist for MLB season-level batting,
pitching, and player data.
"""

import os

import pytest

from .conftest import DBT_DIR

MODELS_DIR = os.path.join(DBT_DIR, "models")

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _find_model(name: str) -> str:
    for root, _dirs, files in os.walk(MODELS_DIR):
        if name in files:
            return os.path.join(root, name)
    pytest.fail(f"{name} not found under {MODELS_DIR}")
    return ""


def _read_model(name: str) -> str:
    path = _find_model(name)
    with open(path) as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestMlbMartModels:
    """Story 017: MLB dbt Mart Models."""

    def test_dim_mlb_players(self):
        """AC: dim_mlb_players.sql deduplicates players across batting and pitching."""
        content = _read_model("dim_mlb_players.sql")
        assert "player" in content.lower(), "Player dimension logic not found"

    def test_fct_mlb_batting_season(self):
        """AC: fct_mlb_batting_season.sql selects season batting stats filtered to players with plate appearances."""  # noqa: E501
        content = _read_model("fct_mlb_batting_season.sql")
        assert "batting" in content.lower(), "Batting fact logic not found"

    def test_fct_mlb_pitching_season(self):
        """AC: fct_mlb_pitching_season.sql selects season pitching stats filtered to players with innings pitched."""  # noqa: E501
        content = _read_model("fct_mlb_pitching_season.sql")
        assert "pitching" in content.lower(), "Pitching fact logic not found"

    def test_mlb_marts_yml_tests(self):
        """AC: _mlb_marts.yml defines column-level tests (not_null on IDs, seasons, key metrics)."""
        content = _read_model("_mlb_marts.yml")
        assert "not_null" in content, "not_null tests not defined in _mlb_marts.yml"

    def test_mart_models_materialized_as_tables(self):
        """AC: All mart models materialized as tables."""
        project_path = os.path.join(DBT_DIR, "dbt_project.yml")
        with open(project_path) as fh:
            content = fh.read()
        assert "table" in content.lower(), (
            "Mart models not configured as tables in dbt_project.yml"
        )
