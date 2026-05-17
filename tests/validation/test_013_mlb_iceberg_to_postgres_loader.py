"""Validation tests for Story 013 – MLB Iceberg-to-Postgres Loader.

Verifies that a loader exists to read Iceberg tables and write them to
PostgreSQL for dbt transformation.
"""

import os

import pytest

from .conftest import SRC_DIR

MLB_DIR = os.path.join(SRC_DIR, "domains", "mlb")

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _find_module(name: str) -> str:
    for root, _dirs, files in os.walk(MLB_DIR):
        if name in files:
            return os.path.join(root, name)
    pytest.fail(f"{name} not found under {MLB_DIR}")
    return ""


def _read_module(name: str) -> str:
    path = _find_module(name)
    with open(path) as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestMlbIcebergToPostgresLoader:
    """Story 013: MLB Iceberg-to-Postgres Loader."""

    def test_loader_reads_iceberg_via_spark(self):
        """AC: iceberg_to_postgres.py reads each MLB Iceberg table via Spark."""
        content = _read_module("iceberg_to_postgres.py")
        assert "spark" in content.lower(), "Spark usage not found in loader"

    def test_converts_to_pandas_and_writes(self):
        """AC: Converts to pandas and writes to raw_mlb PostgreSQL schema."""
        content = _read_module("iceberg_to_postgres.py")
        assert "pandas" in content.lower() or "to_pandas" in content or "toPandas" in content, (
            "Pandas conversion not found"
        )
        assert "raw_mlb" in content, "raw_mlb schema not referenced"

    def test_supports_all_four_tables(self):
        """AC: Supports all 4 MLB tables (statcast, batting, pitching, schedules)."""
        content = _read_module("iceberg_to_postgres.py")
        for table in ["statcast", "batting", "pitching", "schedules"]:
            assert table in content.lower(), f"Table '{table}' not supported in loader"

    def test_idempotent_loads(self):
        """AC: Uses if_exists='replace' for idempotent loads."""
        content = _read_module("iceberg_to_postgres.py")
        assert "replace" in content, "if_exists='replace' not found for idempotent loads"

    def test_load_all_convenience_function(self):
        """AC: load_all_to_postgres() convenience function loads all tables."""
        content = _read_module("iceberg_to_postgres.py")
        assert "load_all_to_postgres" in content, "load_all_to_postgres function not found"
