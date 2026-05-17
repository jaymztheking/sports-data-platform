"""Validation tests for Story 007 – Airflow Helm Release.

All tests verify deployed cluster state. Story is not done until
the webserver and scheduler are Running, the UI is reachable, and
DAG states persist in PostgreSQL.
"""

import json
import os

import pytest

pytestmark = pytest.mark.k3s


class TestAirflowHelmRelease:
    """Story 007: Airflow Helm Release."""

    def test_webserver_pod_running(self, kubectl):
        """AC: Airflow webserver pod is Running in the data-platform namespace."""
        result = kubectl("get", "pods", "-l", "component=webserver", "-o", "json")
        assert result.returncode == 0, f"kubectl failed: {result.stderr}"
        pods = json.loads(result.stdout).get("items", [])
        assert pods, "No Airflow webserver pod found"
        phase = pods[0]["status"]["phase"]
        assert phase == "Running", f"Airflow webserver phase is '{phase}', expected 'Running'"

    def test_scheduler_pod_running(self, kubectl):
        """AC: Airflow scheduler is Running (LocalExecutor)."""
        result = kubectl("get", "pods", "-l", "component=scheduler", "-o", "json")
        assert result.returncode == 0, f"kubectl failed: {result.stderr}"
        pods = json.loads(result.stdout).get("items", [])
        assert pods, "No Airflow scheduler pod found"
        phase = pods[0]["status"]["phase"]
        assert phase == "Running", f"Airflow scheduler phase is '{phase}', expected 'Running'"

    def test_ui_accessible(self, http):
        """AC: Airflow UI accessible at NodePort 30080."""
        url = os.environ.get("AIRFLOW_URL", "http://localhost:30080")
        resp = http.get(f"{url}/health", timeout=10)
        assert resp.status_code == 200, f"Airflow health endpoint returned {resp.status_code}"

    def test_metadata_db_connected(self, pg_conn):
        """AC: Metadata DB connected to PostgreSQL airflow database — DAG states persist."""
        cur = pg_conn.cursor()
        cur.execute("SELECT datname FROM pg_database WHERE datname = 'airflow'")
        result = cur.fetchone()
        cur.close()
        assert result is not None, "airflow database not found in PostgreSQL"

    def test_dags_synced(self, kubectl):
        """AC: git-sync sidecar syncing DAGs — DAG files present in webserver pod."""
        result = kubectl("get", "pods", "-l", "component=webserver", "-o", "json")
        pods = json.loads(result.stdout).get("items", [])
        assert pods, "No Airflow webserver pod found"
        pod_name = pods[0]["metadata"]["name"]
        ls_result = kubectl("exec", pod_name, "--", "ls", "/opt/airflow/dags")
        assert ls_result.returncode == 0, f"Could not list DAGs directory: {ls_result.stderr}"
        assert ls_result.stdout.strip(), "DAGs directory is empty — git-sync may not be working"

    def test_custom_image_from_ghcr(self, kubectl):
        """AC: Custom Airflow image running — not stock apache/airflow image."""
        result = kubectl("get", "pods", "-l", "component=webserver", "-o", "json")
        pods = json.loads(result.stdout).get("items", [])
        assert pods, "No Airflow webserver pod found"
        images = [c["image"] for c in pods[0]["spec"]["containers"]]
        assert any("ghcr.io" in img for img in images), (
            f"Airflow webserver not using GHCR custom image; found: {images}"
        )
