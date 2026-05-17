"""Validation tests for Story 004 – MinIO Helm Release.

Verifies that MinIO is deployed via Helm on K3s with correct buckets,
NodePort, and persistence.
"""

import json
import os

import pytest

from .conftest import HELM_VALUES_DIR, TERRAFORM_DIR

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _read_tf() -> str:
    path = os.path.join(TERRAFORM_DIR, "minio.tf")
    assert os.path.isfile(path), "minio.tf does not exist"
    with open(path) as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# Local file checks
# ---------------------------------------------------------------------------


class TestMinioTerraformFile:
    """Story 004: MinIO Helm Release – Terraform file checks."""

    def test_helm_release_resource(self):
        """AC: minio.tf defines a helm_release using minio/minio chart."""
        content = _read_tf()
        assert "helm_release" in content, "No helm_release resource in minio.tf"
        assert "minio" in content.lower(), "minio chart not referenced"

    def test_standalone_mode(self):
        """AC: Helm values configure standalone mode."""
        values_path = os.path.join(HELM_VALUES_DIR, "minio-values.yaml")
        with open(values_path) as fh:
            content = fh.read()
        assert "standalone" in content.lower(), "Standalone mode not configured in minio-values.yaml"

    def test_buckets_auto_created(self):
        """AC: Buckets auto-created: bronze, mlflow-artifacts, spark-warehouse."""
        values_path = os.path.join(HELM_VALUES_DIR, "minio-values.yaml")
        with open(values_path) as fh:
            content = fh.read()
        for bucket in ["bronze", "mlflow-artifacts", "spark-warehouse"]:
            assert bucket in content, f"Bucket '{bucket}' not found in minio-values.yaml"

    def test_console_nodeport(self):
        """AC: Console exposed via NodePort (30090)."""
        values_path = os.path.join(HELM_VALUES_DIR, "minio-values.yaml")
        with open(values_path) as fh:
            content = fh.read()
        assert "30090" in content, "NodePort 30090 not found in minio-values.yaml"

    def test_persistence_enabled(self):
        """AC: Persistence enabled (10Gi)."""
        values_path = os.path.join(HELM_VALUES_DIR, "minio-values.yaml")
        with open(values_path) as fh:
            content = fh.read()
        assert "10Gi" in content, "Persistence 10Gi not found in minio-values.yaml"

    def test_password_via_sensitive_variable(self):
        """AC: Root password injected via Terraform sensitive variable."""
        content = _read_tf()
        assert "var." in content, "No Terraform variable reference found for root password"


# ---------------------------------------------------------------------------
# Cluster-dependent checks
# ---------------------------------------------------------------------------


@pytest.mark.k3s
class TestMinioCluster:
    """Story 004: MinIO Helm Release – cluster checks."""

    def test_minio_pod_running(self, kubectl):
        """AC (runtime): MinIO pod is running in the cluster."""
        result = kubectl("get", "pods", "-l", "app=minio", "-o", "json")
        assert result.returncode == 0, f"kubectl failed: {result.stderr}"
        data = json.loads(result.stdout)
        pods = data.get("items", [])
        assert len(pods) > 0, "No MinIO pods found"

    def test_buckets_exist(self, s3_client):
        """AC (runtime): Expected buckets exist in MinIO."""
        response = s3_client.list_buckets()
        bucket_names = {b["Name"] for b in response["Buckets"]}
        for expected in ["bronze", "mlflow-artifacts", "spark-warehouse"]:
            assert expected in bucket_names, f"Bucket '{expected}' not found in MinIO"

    def test_console_accessible(self, http):
        """AC (runtime): MinIO console is reachable on NodePort 30090."""
        minio_url = os.environ.get("MINIO_CONSOLE_URL", "http://localhost:30090")
        resp = http.get(minio_url, timeout=10)
        assert resp.status_code < 500, f"MinIO console returned {resp.status_code}"
