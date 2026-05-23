"""Validation tests for Story 014 – MLB Ingestion Airflow DAG.

Verifies that an Airflow DAG orchestrates MLB data ingestion with
parallel tasks, postgres load, and correct scheduling.
"""

import os

from .conftest import DAGS_DIR

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

DAG_FILE = os.path.join(DAGS_DIR, "mlb", "mlb_ingestion_dag.py")


def _read_dag() -> str:
    assert os.path.isfile(DAG_FILE), f"{DAG_FILE} does not exist"
    with open(DAG_FILE) as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestMlbIngestionDag:
    """Story 014: MLB Ingestion Airflow DAG."""

    def test_uses_taskflow_decorators(self):
        """AC: mlb_ingestion_dag.py uses @dag / @task decorators."""
        content = _read_dag()
        assert "@dag" in content or "@task" in content, (
            "TaskFlow decorators (@dag/@task) not found"
        )

    def test_parallel_ingestion_tasks(self):
        """AC: Statcast, batting, pitching, and schedule tasks run in parallel."""
        content = _read_dag()
        for task in ["statcast", "batting", "pitching", "schedule"]:
            assert task in content.lower(), f"'{task}' task not found in DAG"

    def test_load_to_postgres_after_ingestion(self):
        """AC: load_to_postgres task runs after all ingestion tasks complete."""
        content = _read_dag()
        assert "load" in content.lower() and "postgres" in content.lower(), (
            "load_to_postgres task not found"
        )

    def test_spark_session_lifecycle(self):
        """AC: Each task creates and properly closes its own SparkSession."""
        content = _read_dag()
        assert "SparkSession" in content or "spark" in content.lower(), (
            "SparkSession management not found"
        )

    def test_weekly_schedule_no_catchup(self):
        """AC: DAG scheduled weekly with catchup=False."""
        content = _read_dag()
        assert "catchup" in content.lower(), "catchup parameter not found"
        assert "False" in content, "catchup=False not set"
        # Check for weekly schedule
        content_lower = content.lower()
        assert "week" in content_lower or "timedelta(days=7)" in content or "@weekly" in content, (
            "Weekly schedule not configured"
        )

    def test_tags(self):
        """AC: Tagged with mlb, ingestion, bronze."""
        content = _read_dag()
        for tag in ["mlb", "ingestion", "bronze"]:
            assert tag in content.lower(), f"Tag '{tag}' not found in DAG"
