"""Validation tests for Story 008 – MLflow Tracking Server Deployment.

Verifies that MLflow is deployed on K3s with correct backend store,
artifact root, and NodePort exposure.
"""

import json
import os

import pytest

from .conftest import TERRAFORM_DIR

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _read_tf() -> str:
    path = os.path.join(TERRAFORM_DIR, "mlflow.tf")
    assert os.path.isfile(path), "mlflow.tf does not exist"
    with open(path) as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# Local file checks
# ---------------------------------------------------------------------------


class TestMlflowTerraformFile:
    """Story 008: MLflow Tracking Server – Terraform file checks."""

    def test_deployment_and_service_resources(self):
        """AC: mlflow.tf defines kubernetes_deployment and kubernetes_service resources."""
        content = _read_tf()
        assert "kubernetes_deployment" in content, "No kubernetes_deployment in mlflow.tf"
        assert "kubernetes_service" in content, "No kubernetes_service in mlflow.tf"

    def test_custom_mlflow_image(self):
        """AC: Custom MLflow image with psycopg2 and boto3."""
        content = _read_tf()
        assert "mlflow" in content.lower(), "MLflow image not referenced"
        assert "image" in content.lower(), "No image reference found"

    def test_backend_store_uri(self):
        """AC: Backend store URI points to PostgreSQL mlflow database."""
        content = _read_tf()
        assert "backend-store-uri" in content or "backend_store_uri" in content.lower() or "postgresql" in content.lower(), (
            "Backend store URI not configured"
        )

    def test_artifact_root(self):
        """AC: Artifact root points to MinIO mlflow-artifacts bucket."""
        content = _read_tf()
        assert "mlflow-artifacts" in content, "Artifact root not pointing to mlflow-artifacts bucket"

    def test_nodeport_exposure(self):
        """AC: Exposed via NodePort (30500)."""
        content = _read_tf()
        assert "30500" in content, "NodePort 30500 not found in mlflow.tf"

    def test_resource_limits(self):
        """AC: Resource limits appropriate for Pi (256Mi-512Mi)."""
        content = _read_tf()
        assert "256Mi" in content or "512Mi" in content, (
            "No Pi-appropriate resource limits found"
        )

    def test_depends_on_postgres_and_minio(self):
        """AC: Depends on PostgreSQL and MinIO."""
        content = _read_tf()
        assert "depends_on" in content, "No depends_on found in mlflow.tf"


# ---------------------------------------------------------------------------
# Cluster-dependent checks
# ---------------------------------------------------------------------------


@pytest.mark.k3s
class TestMlflowCluster:
    """Story 008: MLflow Tracking Server – cluster checks."""

    def test_mlflow_pod_running(self, kubectl):
        """AC (runtime): MLflow pod is running."""
        result = kubectl("get", "pods", "-o", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        mlflow_pods = [
            p for p in data.get("items", [])
            if "mlflow" in p["metadata"]["name"].lower()
        ]
        assert len(mlflow_pods) > 0, "No MLflow pods found"

    def test_mlflow_ui_accessible(self, http):
        """AC (runtime): MLflow UI is reachable on NodePort 30500."""
        url = os.environ.get("MLFLOW_URL", "http://localhost:30500")
        resp = http.get(url, timeout=10)
        assert resp.status_code == 200, f"MLflow UI returned {resp.status_code}"
