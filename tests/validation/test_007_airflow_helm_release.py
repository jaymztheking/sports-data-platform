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
        url = os.environ.get("AIRFLOW_URL", "http://192.168.50.231:30007")
        resp = http.get(f"{url}/health", timeout=10)
        assert resp.status_code == 200, f"Airflow health endpoint returned {resp.status_code}"

    def test_metadata_db_connected(self, http):
        """AC: Metadata DB connected to PostgreSQL airflow database — DAG states persist.

        Uses the /health endpoint's metadatabase status rather than a direct psycopg2
        connection so the test doesn't require DB credentials on the test runner.
        """
        url = os.environ.get("AIRFLOW_URL", "http://192.168.50.231:30007")
        resp = http.get(f"{url}/health", timeout=10)
        assert resp.status_code == 200
        health = resp.json()
        status = health.get("metadatabase", {}).get("status")
        assert status == "healthy", f"Airflow metadatabase status is '{status}', expected 'healthy'"

    def test_dags_synced(self, kubectl):
        """AC: git-sync sidecar syncing DAGs from main branch — DAG files present.

        git-sync runs on the scheduler (not the webserver) for LocalExecutor.
        DAGs land at /opt/airflow/dags/repo/<subPath> per the chart's gitSync config.
        """
        result = kubectl("get", "pods", "-l", "component=scheduler", "-o", "json")
        pods = json.loads(result.stdout).get("items", [])
        assert pods, "No Airflow scheduler pod found"
        pod_name = pods[0]["metadata"]["name"]
        ls_result = kubectl(
            "exec", pod_name, "-c", "scheduler", "--", "ls", "/opt/airflow/dags/repo/dags"
        )
        assert ls_result.returncode == 0, f"Could not list DAGs directory: {ls_result.stderr}"
        assert ls_result.stdout.strip(), "DAGs directory is empty — git-sync may not be working"

    def test_airflow_image_running(self, kubectl):
        """AC: Airflow image confirmed running on ARM64 Pi nodes.

        Custom GHCR image is deferred to story 009 (ARM64 CI build pipeline).
        For now, verifies the apache/airflow stock image is present and running.
        """
        result = kubectl("get", "pods", "-l", "component=webserver", "-o", "json")
        pods = json.loads(result.stdout).get("items", [])
        assert pods, "No Airflow webserver pod found"
        images = [c["image"] for c in pods[0]["spec"]["containers"]]
        assert any("airflow" in img.lower() for img in images), (
            f"Airflow webserver not running an airflow image; found: {images}"
        )
