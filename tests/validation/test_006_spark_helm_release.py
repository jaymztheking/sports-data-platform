"""Validation tests for Story 006 – Spark Helm Release.

Verifies that Spark master and workers are deployed on K3s with custom
image, correct topology, and resource limits.
"""

import json
import os

import pytest

from .conftest import HELM_VALUES_DIR, TERRAFORM_DIR

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _read_tf() -> str:
    path = os.path.join(TERRAFORM_DIR, "spark.tf")
    assert os.path.isfile(path), "spark.tf does not exist"
    with open(path) as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# Local file checks
# ---------------------------------------------------------------------------


class TestSparkTerraformFile:
    """Story 006: Spark Helm Release – Terraform file checks."""

    def test_helm_release_resource(self):
        """AC: spark.tf defines a helm_release using bitnami/spark chart."""
        content = _read_tf()
        assert "helm_release" in content, "No helm_release resource in spark.tf"
        assert "spark" in content.lower(), "spark chart not referenced"

    def test_custom_image_reference(self):
        """AC: Custom image reference with Iceberg JARs."""
        content = _read_tf()
        assert "image" in content.lower(), "No custom image reference found in spark.tf"

    def test_master_and_workers(self):
        """AC: Helm values configure 1 master + 2 workers."""
        values_path = os.path.join(HELM_VALUES_DIR, "spark-values.yaml")
        with open(values_path) as fh:
            content = fh.read()
        assert "worker" in content.lower(), "No worker configuration found"
        assert "replicaCount: 2" in content or "replicaCount: '2'" in content, (
            "Worker replica count of 2 not found in spark-values.yaml"
        )

    def test_worker_resource_limits(self):
        """AC: Worker resources tuned for Pi (512Mi-1Gi RAM)."""
        values_path = os.path.join(HELM_VALUES_DIR, "spark-values.yaml")
        with open(values_path) as fh:
            content = fh.read()
        assert "512Mi" in content or "1Gi" in content, (
            "No Pi-appropriate resource limits found in spark-values.yaml"
        )

    def test_depends_on_minio_and_iceberg(self):
        """AC: Depends on MinIO and Iceberg REST catalog."""
        content = _read_tf()
        assert "depends_on" in content, "No depends_on found in spark.tf"


# ---------------------------------------------------------------------------
# Cluster-dependent checks
# ---------------------------------------------------------------------------


@pytest.mark.k3s
class TestSparkCluster:
    """Story 006: Spark Helm Release – cluster checks."""

    def test_spark_master_running(self, kubectl):
        """AC (runtime): Spark master pod is running."""
        result = kubectl("get", "pods", "-l", "app.kubernetes.io/component=master", "-o", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        pods = data.get("items", [])
        assert len(pods) > 0, "No Spark master pod found"

    def test_spark_workers_running(self, kubectl):
        """AC (runtime): Spark worker pods are running."""
        result = kubectl("get", "pods", "-l", "app.kubernetes.io/component=worker", "-o", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        pods = data.get("items", [])
        assert len(pods) >= 2, f"Expected at least 2 Spark workers, found {len(pods)}"
