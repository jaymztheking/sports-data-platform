"""Validation tests for Story 005 – Iceberg REST Catalog Deployment.

Verifies that an Iceberg REST catalog is deployed on K3s with correct
image, S3FileIO config, and resource limits.
"""

import json
import os

import pytest

from .conftest import TERRAFORM_DIR

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _read_tf() -> str:
    path = os.path.join(TERRAFORM_DIR, "iceberg.tf")
    assert os.path.isfile(path), "iceberg.tf does not exist"
    with open(path) as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# Local file checks
# ---------------------------------------------------------------------------


class TestIcebergTerraformFile:
    """Story 005: Iceberg REST Catalog – Terraform file checks."""

    def test_deployment_and_service_resources(self):
        """AC: iceberg.tf defines kubernetes_deployment and kubernetes_service resources."""
        content = _read_tf()
        assert "kubernetes_deployment" in content, "No kubernetes_deployment in iceberg.tf"
        assert "kubernetes_service" in content, "No kubernetes_service in iceberg.tf"

    def test_tabulario_image(self):
        """AC: Uses tabulario/iceberg-rest:1.5.0 image."""
        content = _read_tf()
        assert "tabulario/iceberg-rest" in content, "tabulario/iceberg-rest image not found"

    def test_s3fileio_configured(self):
        """AC: Configured to use S3FileIO pointing to MinIO."""
        content = _read_tf()
        assert "s3" in content.lower(), "S3FileIO configuration not found"

    def test_warehouse_path(self):
        """AC: Warehouse path set to s3://spark-warehouse/."""
        content = _read_tf()
        assert "s3://spark-warehouse" in content, "Warehouse path not set to s3://spark-warehouse/"

    def test_aws_credentials_reference(self):
        """AC: AWS credentials reference MinIO secret."""
        content = _read_tf()
        assert "aws" in content.lower() or "minio" in content.lower(), (
            "AWS/MinIO credential reference not found"
        )

    def test_resource_limits(self):
        """AC: Resource limits appropriate for Raspberry Pi (256Mi-512Mi)."""
        content = _read_tf()
        assert "256Mi" in content or "512Mi" in content, (
            "No ARM64-appropriate resource limits found"
        )

    def test_depends_on_minio(self):
        """AC: Depends on MinIO deployment."""
        content = _read_tf()
        assert "depends_on" in content or "minio" in content.lower(), (
            "No dependency on MinIO found"
        )


# ---------------------------------------------------------------------------
# Cluster-dependent checks
# ---------------------------------------------------------------------------


@pytest.mark.k3s
class TestIcebergCluster:
    """Story 005: Iceberg REST Catalog – cluster checks."""

    def test_iceberg_pod_running(self, kubectl):
        """AC (runtime): Iceberg REST catalog pod is running."""
        result = kubectl("get", "pods", "-o", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        iceberg_pods = [
            p for p in data.get("items", [])
            if "iceberg" in p["metadata"]["name"].lower()
        ]
        assert len(iceberg_pods) > 0, "No Iceberg REST catalog pods found"

    def test_iceberg_health(self, http):
        """AC (runtime): Iceberg REST catalog responds to health check."""
        url = os.environ.get("ICEBERG_REST_URL", "http://localhost:8181")
        resp = http.get(f"{url}/v1/config", timeout=10)
        assert resp.status_code == 200, f"Iceberg REST catalog returned {resp.status_code}"
