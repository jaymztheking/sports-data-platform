"""Validation tests for Story 007 – Airflow Helm Release.

Verifies that Airflow is deployed on K3s with LocalExecutor, custom image,
git-sync, NodePort, and correct dependency wiring.
"""

import json
import os

import pytest

from .conftest import HELM_VALUES_DIR, TERRAFORM_DIR

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _read_tf() -> str:
    path = os.path.join(TERRAFORM_DIR, "airflow.tf")
    assert os.path.isfile(path), "airflow.tf does not exist"
    with open(path) as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# Local file checks
# ---------------------------------------------------------------------------


class TestAirflowTerraformFile:
    """Story 007: Airflow Helm Release – Terraform file checks."""

    def test_helm_release_resource(self):
        """AC: airflow.tf defines a helm_release using apache-airflow chart."""
        content = _read_tf()
        assert "helm_release" in content, "No helm_release resource in airflow.tf"
        assert "airflow" in content.lower(), "airflow chart not referenced"

    def test_local_executor(self):
        """AC: LocalExecutor configured."""
        values_path = os.path.join(HELM_VALUES_DIR, "airflow-values.yaml")
        with open(values_path) as fh:
            content = fh.read()
        assert "LocalExecutor" in content, "LocalExecutor not configured in airflow-values.yaml"

    def test_custom_image_reference(self):
        """AC: Custom image reference with project dependencies."""
        content = _read_tf()
        assert "image" in content.lower(), "No custom image reference found"

    def test_git_sync_sidecar(self):
        """AC: git-sync sidecar for DAGs from main branch."""
        values_path = os.path.join(HELM_VALUES_DIR, "airflow-values.yaml")
        with open(values_path) as fh:
            content = fh.read()
        assert "git" in content.lower() and "sync" in content.lower(), (
            "git-sync configuration not found in airflow-values.yaml"
        )

    def test_webserver_nodeport(self):
        """AC: Webserver exposed via NodePort (30080)."""
        values_path = os.path.join(HELM_VALUES_DIR, "airflow-values.yaml")
        with open(values_path) as fh:
            content = fh.read()
        assert "30080" in content, "NodePort 30080 not found in airflow-values.yaml"

    def test_metadata_connection_to_postgres(self):
        """AC: Metadata connection points to PostgreSQL airflow database."""
        content = _read_tf()
        assert "airflow" in content.lower() and "postgres" in content.lower(), (
            "PostgreSQL airflow connection not found"
        )

    def test_env_vars_spark_minio(self):
        """AC: Environment variables configure Spark and MinIO connections."""
        content = _read_tf()
        # Should reference spark or minio in env config
        content_lower = content.lower()
        assert "spark" in content_lower or "minio" in content_lower, (
            "No Spark/MinIO env var configuration found"
        )

    def test_fernet_key_sensitive(self):
        """AC: Fernet key injected via Terraform sensitive variable."""
        content = _read_tf()
        assert "fernet" in content.lower(), "Fernet key configuration not found"

    def test_depends_on_postgres_and_minio(self):
        """AC: Depends on PostgreSQL and MinIO."""
        content = _read_tf()
        assert "depends_on" in content, "No depends_on found in airflow.tf"


# ---------------------------------------------------------------------------
# Cluster-dependent checks
# ---------------------------------------------------------------------------


@pytest.mark.k3s
class TestAirflowCluster:
    """Story 007: Airflow Helm Release – cluster checks."""

    def test_airflow_webserver_running(self, kubectl):
        """AC (runtime): Airflow webserver pod is running."""
        result = kubectl("get", "pods", "-l", "component=webserver", "-o", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        pods = data.get("items", [])
        assert len(pods) > 0, "No Airflow webserver pod found"

    def test_airflow_web_ui_accessible(self, http):
        """AC (runtime): Airflow UI is reachable on NodePort 30080."""
        url = os.environ.get("AIRFLOW_URL", "http://localhost:30080")
        resp = http.get(f"{url}/health", timeout=10)
        assert resp.status_code == 200, f"Airflow health endpoint returned {resp.status_code}"
