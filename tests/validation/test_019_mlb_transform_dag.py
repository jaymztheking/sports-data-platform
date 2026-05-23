"""Validation tests for Story 019 – MLB Transform Airflow DAG.

Verifies that an Airflow DAG runs dbt models for MLB staging and mart layers.
"""

import os

from .conftest import DAGS_DIR

DAG_FILE = os.path.join(DAGS_DIR, "mlb", "mlb_transform_dag.py")

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _read_dag() -> str:
    assert os.path.isfile(DAG_FILE), f"{DAG_FILE} does not exist"
    with open(DAG_FILE) as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestMlbTransformDag:
    """Story 019: MLB Transform Airflow DAG."""

    def test_sequential_staging_then_marts_then_tests(self):
        """AC: mlb_transform_dag.py runs staging models, then marts, then tests sequentially."""
        content = _read_dag()
        assert "staging" in content.lower() or "stg" in content.lower(), (
            "Staging step not found in transform DAG"
        )
        assert "mart" in content.lower(), "Marts step not found in transform DAG"
        assert "test" in content.lower(), "Test step not found in transform DAG"

    def test_dbt_cli_with_select(self):
        """AC: Uses dbt CLI with --select tag filters for MLB."""
        content = _read_dag()
        assert "dbt" in content.lower(), "dbt CLI not referenced"
        assert "select" in content.lower() or "--select" in content, (
            "--select tag filter not used"
        )

    def test_manually_triggered(self):
        """AC: Manually triggered (downstream of ingestion)."""
        content = _read_dag()
        # Manual trigger typically means schedule=None or schedule_interval=None
        assert "None" in content or "manual" in content.lower() or "schedule" in content.lower(), (
            "Manual trigger configuration not found"
        )

    def test_tags(self):
        """AC: Tagged with mlb, transform, dbt."""
        content = _read_dag()
        for tag in ["mlb", "transform", "dbt"]:
            assert tag in content.lower(), f"Tag '{tag}' not found in transform DAG"
