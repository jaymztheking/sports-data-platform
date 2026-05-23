"""Validation tests for Story 003 – PostgreSQL Helm Release.

All tests verify deployed cluster state. Story is not done until
PostgreSQL is Running on K3s with the correct databases, schemas, and PVC.
"""

import json

import pytest

pytestmark = pytest.mark.k3s


class TestPostgresqlHelmRelease:
    """Story 003: PostgreSQL Helm Release."""

    def test_pod_running(self, kubectl):
        """AC: PostgreSQL pod is Running in the data-platform namespace."""
        result = kubectl("get", "pods", "-l", "app.kubernetes.io/name=postgresql", "-o", "json")
        assert result.returncode == 0, f"kubectl failed: {result.stderr}"
        pods = json.loads(result.stdout).get("items", [])
        assert pods, "No PostgreSQL pods found"
        phase = pods[0]["status"]["phase"]
        assert phase == "Running", f"PostgreSQL pod phase is '{phase}', expected 'Running'"

    def test_accepts_connections(self, pg_conn):
        """AC: PostgreSQL accepts connections."""
        cur = pg_conn.cursor()
        cur.execute("SELECT 1")
        assert cur.fetchone()[0] == 1
        cur.close()

    def test_databases_exist(self, pg_conn):
        """AC: Databases airflow and mlflow exist."""
        cur = pg_conn.cursor()
        cur.execute("SELECT datname FROM pg_database WHERE datname IN ('airflow', 'mlflow')")
        dbs = {row[0] for row in cur.fetchall()}
        cur.close()
        assert "airflow" in dbs, "airflow database not found"
        assert "mlflow" in dbs, "mlflow database not found"

    def test_schemas_exist(self, pg_conn):
        """AC: Schemas raw_mlb, raw_nfl, raw_nba, raw_nhl, staging, marts exist."""
        cur = pg_conn.cursor()
        cur.execute("SELECT schema_name FROM information_schema.schemata")
        schemas = {row[0] for row in cur.fetchall()}
        cur.close()
        for s in ["raw_mlb", "raw_nfl", "raw_nba", "raw_nhl", "staging", "marts"]:
            assert s in schemas, f"Schema '{s}' not found in PostgreSQL"

    def test_pvc_bound(self, kubectl):
        """AC: 5Gi PVC is bound."""
        result = kubectl("get", "pvc", "-l", "app.kubernetes.io/name=postgresql", "-o", "json")
        assert result.returncode == 0, f"kubectl failed: {result.stderr}"
        pvcs = json.loads(result.stdout).get("items", [])
        assert pvcs, "No PostgreSQL PVC found"
        for pvc in pvcs:
            status = pvc["status"]["phase"]
            name = pvc["metadata"]["name"]
            assert status == "Bound", f"PVC '{name}' is '{status}', expected 'Bound'"

    def test_resource_limits_set(self, kubectl):
        """AC: Resource limits are ARM64-appropriate (256Mi request / 512Mi limit)."""
        result = kubectl("get", "pods", "-l", "app.kubernetes.io/name=postgresql", "-o", "json")
        pods = json.loads(result.stdout).get("items", [])
        assert pods, "No PostgreSQL pods found"
        containers = pods[0]["spec"]["containers"]
        assert containers, "No containers in PostgreSQL pod"
        resources = containers[0].get("resources", {})
        limits = resources.get("limits", {})
        assert "memory" in limits, "No memory limit set on PostgreSQL container"
