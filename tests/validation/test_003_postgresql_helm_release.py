"""Validation tests for Story 003 – PostgreSQL Helm Release.

Verifies that PostgreSQL is deployed via Helm on K3s with the correct
databases, schemas, resource limits, and persistence.
"""

import json
import os
import subprocess

import pytest

from .conftest import HELM_VALUES_DIR, TERRAFORM_DIR

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _read_tf() -> str:
    path = os.path.join(TERRAFORM_DIR, "postgres.tf")
    assert os.path.isfile(path), "postgres.tf does not exist"
    with open(path) as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# Local file checks (no cluster needed)
# ---------------------------------------------------------------------------


class TestPostgresqlTerraformFile:
    """Story 003: PostgreSQL Helm Release – Terraform file checks."""

    def test_helm_release_resource(self):
        """AC: postgres.tf defines a helm_release using bitnami/postgresql chart."""
        content = _read_tf()
        assert "helm_release" in content, "No helm_release resource in postgres.tf"
        assert "postgresql" in content.lower(), "bitnami/postgresql chart not referenced"

    def test_init_sql_creates_databases(self):
        """AC: Init SQL script creates databases: airflow, mlflow."""
        content = _read_tf()
        for db in ["airflow", "mlflow"]:
            assert db in content.lower(), f"Database '{db}' not found in init SQL"

    def test_init_sql_creates_schemas(self):
        """AC: Init SQL script creates schemas: raw_mlb, raw_nfl, raw_nba, raw_nhl, staging, marts."""
        content = _read_tf()
        for schema in ["raw_mlb", "raw_nfl", "raw_nba", "raw_nhl", "staging", "marts"]:
            assert schema in content.lower(), f"Schema '{schema}' not found in init SQL"

    def test_configmap_mounts_init_script(self):
        """AC: ConfigMap mounts the init script."""
        content = _read_tf()
        assert "configmap" in content.lower() or "initdb" in content.lower(), (
            "No ConfigMap or initdb configuration found"
        )

    def test_resource_limits_arm64(self):
        """AC: Helm values set ARM64-appropriate resource limits (256Mi-512Mi)."""
        values_path = os.path.join(HELM_VALUES_DIR, "postgres-values.yaml")
        with open(values_path) as fh:
            content = fh.read()
        assert "256Mi" in content or "512Mi" in content, (
            "No ARM64-appropriate resource limits found in postgres-values.yaml"
        )

    def test_persistence_enabled(self):
        """AC: Persistence enabled (5Gi)."""
        values_path = os.path.join(HELM_VALUES_DIR, "postgres-values.yaml")
        with open(values_path) as fh:
            content = fh.read()
        assert "5Gi" in content, "Persistence 5Gi not found in postgres-values.yaml"

    def test_password_via_sensitive_variable(self):
        """AC: Password injected via Terraform sensitive variable."""
        content = _read_tf()
        assert "var." in content, "No Terraform variable reference found for password"


# ---------------------------------------------------------------------------
# Cluster-dependent checks
# ---------------------------------------------------------------------------


@pytest.mark.k3s
class TestPostgresqlCluster:
    """Story 003: PostgreSQL Helm Release – cluster checks."""

    def test_postgres_pod_running(self, kubectl):
        """AC (runtime): PostgreSQL pod is running in the cluster."""
        result = kubectl("get", "pods", "-l", "app.kubernetes.io/name=postgresql", "-o", "json")
        assert result.returncode == 0, f"kubectl failed: {result.stderr}"
        data = json.loads(result.stdout)
        pods = data.get("items", [])
        assert len(pods) > 0, "No PostgreSQL pods found"
        phase = pods[0]["status"]["phase"]
        assert phase == "Running", f"PostgreSQL pod phase is {phase}, expected Running"

    def test_databases_exist(self, pg_conn):
        """AC (runtime): databases airflow and mlflow exist."""
        cur = pg_conn.cursor()
        cur.execute("SELECT datname FROM pg_database WHERE datname IN ('airflow', 'mlflow')")
        dbs = {row[0] for row in cur.fetchall()}
        cur.close()
        assert "airflow" in dbs, "airflow database not found"
        assert "mlflow" in dbs, "mlflow database not found"

    def test_schemas_exist(self, pg_conn):
        """AC (runtime): expected schemas exist."""
        cur = pg_conn.cursor()
        cur.execute("SELECT schema_name FROM information_schema.schemata")
        schemas = {row[0] for row in cur.fetchall()}
        cur.close()
        for s in ["raw_mlb", "raw_nfl", "raw_nba", "raw_nhl", "staging", "marts"]:
            assert s in schemas, f"Schema '{s}' not found in PostgreSQL"
