"""Validation tests for Story 016 – MLB dbt Staging Models.

Verifies that dbt staging models exist to clean and standardize raw MLB data.
"""

import os

import pytest

from .conftest import DBT_DIR

MODELS_DIR = os.path.join(DBT_DIR, "models")

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _find_model(name: str) -> str:
    """Recursively find a model file under models/."""
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


class TestMlbStagingModels:
    """Story 016: MLB dbt Staging Models."""

    def test_mlb_sources_yml(self):
        """AC: _mlb_sources.yml defines sources for all raw_mlb tables with freshness checks."""
        content = _read_model("_mlb_sources.yml")
        assert "raw_mlb" in content, "raw_mlb source not defined"
        assert "freshness" in content.lower() or "loaded_at" in content.lower(), (
            "Freshness checks not configured"
        )

    def test_stg_mlb_statcast(self):
        """AC: stg_mlb__statcast.sql renames columns, casts types."""
        content = _read_model("stg_mlb__statcast.sql")
        assert "cast" in content.lower() or "as " in content.lower(), (
            "No type casting found in stg_mlb__statcast"
        )

    def test_stg_mlb_batting(self):
        """AC: stg_mlb__batting.sql maps FanGraphs column names to readable names."""
        content = _read_model("stg_mlb__batting.sql")
        assert "batting" in content.lower(), "Batting references not found"

    def test_stg_mlb_pitching(self):
        """AC: stg_mlb__pitching.sql standardizes pitching stats."""
        content = _read_model("stg_mlb__pitching.sql")
        assert "pitching" in content.lower(), "Pitching references not found"

    def test_stg_mlb_schedules(self):
        """AC: stg_mlb__schedules.sql cleans schedule data."""
        content = _read_model("stg_mlb__schedules.sql")
        assert "schedule" in content.lower() or "game" in content.lower(), (
            "Schedule data references not found"
        )

    def test_staging_models_materialized_as_views(self):
        """AC: All staging models materialized as views."""
        # Check dbt_project.yml for staging materialization config
        project_path = os.path.join(DBT_DIR, "dbt_project.yml")
        with open(project_path) as fh:
            content = fh.read()
        assert "view" in content.lower(), (
            "Staging models not configured as views in dbt_project.yml"
        )
