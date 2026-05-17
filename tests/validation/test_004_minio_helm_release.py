"""Validation tests for Story 004 – MinIO Helm Release.

All tests verify deployed cluster state. Story is not done until
MinIO is Running on K3s with the correct buckets, NodePort, and PVC.
"""

import json
import os

import pytest

pytestmark = pytest.mark.k3s


class TestMinioHelmRelease:
    """Story 004: MinIO Helm Release."""

    def test_pod_running(self, kubectl):
        """AC: MinIO pod is Running in the data-platform namespace."""
        result = kubectl("get", "pods", "-l", "app=minio", "-o", "json")
        assert result.returncode == 0, f"kubectl failed: {result.stderr}"
        pods = json.loads(result.stdout).get("items", [])
        assert pods, "No MinIO pods found"
        phase = pods[0]["status"]["phase"]
        assert phase == "Running", f"MinIO pod phase is '{phase}', expected 'Running'"

    def test_console_accessible(self, http):
        """AC: MinIO console accessible at NodePort 30090."""
        url = os.environ.get("MINIO_CONSOLE_URL", "http://localhost:30090")
        resp = http.get(url, timeout=10)
        assert resp.status_code < 500, f"MinIO console returned {resp.status_code}"

    def test_buckets_exist(self, s3_client):
        """AC: Buckets bronze, mlflow-artifacts, spark-warehouse created and accessible."""
        response = s3_client.list_buckets()
        bucket_names = {b["Name"] for b in response["Buckets"]}
        for expected in ["bronze", "mlflow-artifacts", "spark-warehouse"]:
            assert expected in bucket_names, f"Bucket '{expected}' not found in MinIO"

    def test_pvc_bound(self, kubectl):
        """AC: 10Gi PVC is bound."""
        result = kubectl("get", "pvc", "-l", "app=minio", "-o", "json")
        assert result.returncode == 0, f"kubectl failed: {result.stderr}"
        pvcs = json.loads(result.stdout).get("items", [])
        assert pvcs, "No MinIO PVC found"
        for pvc in pvcs:
            status = pvc["status"]["phase"]
            assert status == "Bound", f"PVC '{pvc['metadata']['name']}' is '{status}', expected 'Bound'"

    def test_s3_api_reachable(self, s3_client):
        """AC: S3 API is functional (list-buckets round-trip succeeds)."""
        response = s3_client.list_buckets()
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
