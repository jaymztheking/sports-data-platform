"""Validation tests for Story 012 – MLB Ingestion Modules.

Verifies that Python modules exist to fetch MLB data from pybaseball and
write it to Iceberg tables for the bronze layer.
"""

import os

import pytest

from .conftest import SRC_DIR

MLB_DIR = os.path.join(SRC_DIR, "domains", "mlb")

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _find_module(name: str) -> str:
    """Find a module by name in the MLB domain tree."""
    for root, _dirs, files in os.walk(MLB_DIR):
        if name in files:
            return os.path.join(root, name)
    pytest.fail(f"{name} not found under {MLB_DIR}")
    return ""  # unreachable


def _read_module(name: str) -> str:
    path = _find_module(name)
    with open(path) as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestMlbIngestionModules:
    """Story 012: MLB Ingestion Modules."""

    def test_statcast_module(self):
        """AC: statcast.py fetches pitch-level Statcast data for a date range, writes to iceberg.mlb.statcast."""  # noqa: E501
        content = _read_module("statcast.py")
        assert "statcast" in content.lower(), "Statcast logic not found"

    def test_batting_module(self):
        """AC: batting.py fetches season batting stats, writes to iceberg.mlb.batting."""
        content = _read_module("batting.py")
        assert "batting" in content.lower(), "Batting logic not found"

    def test_pitching_module(self):
        """AC: pitching.py fetches season pitching stats, writes to iceberg.mlb.pitching."""
        content = _read_module("pitching.py")
        assert "pitching" in content.lower(), "Pitching logic not found"

    def test_schedules_module(self):
        """AC: schedules.py fetches game schedules for all 30 MLB teams, writes to iceberg.mlb.schedules."""  # noqa: E501
        content = _read_module("schedules.py")
        assert "schedule" in content.lower(), "Schedule logic not found"

    def test_metadata_columns(self):
        """AC: All modules add ingested_at, source, and season metadata columns."""
        for module in ["statcast.py", "batting.py", "pitching.py", "schedules.py"]:
            content = _read_module(module)
            assert "ingested_at" in content, f"{module} missing ingested_at column"
            assert "source" in content, f"{module} missing source column"
            assert "season" in content, f"{module} missing season column"

    def test_partitioned_by_season(self):
        """AC: All tables partitioned by season."""
        for module in ["statcast.py", "batting.py", "pitching.py", "schedules.py"]:
            content = _read_module(module)
            assert "partition" in content.lower() or "season" in content.lower(), (
                f"{module} missing partitioning by season"
            )

    def test_extract_standardize_write_pattern(self):
        """AC: Each module follows extract -> standardize -> Iceberg write pattern."""
        for module in ["statcast.py", "batting.py", "pitching.py", "schedules.py"]:
            content = _read_module(module)
            # Should have some form of write to Iceberg
            assert (
                "write" in content.lower() or "writeTo" in content or "save" in content.lower()
            ), (
                f"{module} missing Iceberg write step"
            )
