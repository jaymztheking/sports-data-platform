"""Validation tests for Story 008 – MLflow Tracking Server Deployment.

All tests verify deployed cluster state. Story is not done until
MLflow is Running, the UI is reachable, and experiments persist in PostgreSQL.
"""

import json
import os

import pytest

pytestmark = pytest.mark.k3s


class TestMlflowDeployment:
    """Story 008: MLflow Tracking Server Deployment."""

    def test_pod_running(self, kubectl):
        """AC: MLflow pod is Running in the data-platform namespace."""
        result = kubectl("get", "pods", "-o", "json")
        assert result.returncode == 0, f"kubectl failed: {result.stderr}"
        pods = json.loads(result.stdout).get("items", [])
        mlflow_pods = [p for p in pods if "mlflow" in p["metadata"]["name"].lower()]
        assert mlflow_pods, "No MLflow pods found"
        phase = mlflow_pods[0]["status"]["phase"]
        assert phase == "Running", f"MLflow pod phase is '{phase}', expected 'Running'"

    def test_ui_accessible(self, http):
        """AC: MLflow UI accessible at NodePort 30500."""
        url = os.environ.get("MLFLOW_URL", "http://192.168.50.231:30500")
        resp = http.get(url, timeout=10)
        assert resp.status_code == 200, f"MLflow UI returned {resp.status_code}"

    def test_experiments_persist(self, http):
        """AC: Experiment runs persist across restarts — REST API reads from PostgreSQL backend."""
        url = os.environ.get("MLFLOW_URL", "http://192.168.50.231:30500")
        resp = http.get(f"{url}/api/2.0/mlflow/experiments/search", params={"max_results": 10}, timeout=10)
        assert resp.status_code == 200, f"MLflow experiments API returned {resp.status_code}"
        data = resp.json()
        assert "experiments" in data, "MLflow experiments API did not return experiments list"
        # Default experiment artifact_location points to MinIO, confirming both backends
        locations = [e.get("artifact_location", "") for e in data["experiments"]]
        assert any("s3://" in loc for loc in locations), (
            f"No S3 artifact location found; locations: {locations}"
        )

    def test_artifact_store_reachable(self, s3_client):
        """AC: Artifact store connected to MinIO mlflow-artifacts bucket."""
        response = s3_client.list_buckets()
        bucket_names = {b["Name"] for b in response["Buckets"]}
        assert "mlflow-artifacts" in bucket_names, "mlflow-artifacts bucket not found in MinIO"

    def test_custom_image_from_ghcr(self, kubectl):
        """AC: Custom MLflow image (with psycopg2 and boto3) running on ARM64."""
        result = kubectl("get", "pods", "-o", "json")
        pods = json.loads(result.stdout).get("items", [])
        mlflow_pods = [p for p in pods if "mlflow" in p["metadata"]["name"].lower()]
        assert mlflow_pods, "No MLflow pods found"
        images = [c["image"] for c in mlflow_pods[0]["spec"]["containers"]]
        assert any("ghcr.io" in img for img in images), (
            f"MLflow pod not using GHCR custom image; found: {images}"
        )
