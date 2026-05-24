"""Validation tests for Story 044 – Rotate Leaked Secrets.

All tests verify live cluster state: new credentials active, old rejected,
affected services healthy.
"""

import json

import psycopg2
import pytest

pytestmark = pytest.mark.k3s

NAMESPACE = "data-platform"
PG_HOST = "192.168.50.231"
PG_PORT = 30432
PG_USER = "postgres"
OLD_PG_PASSWORD = "!VE@3t79n^Pkkf8UoyXPE1T%"
NEW_PG_PASSWORD = "0WGQM38bwJuuPRgeg6ukZ3OC"


class TestRotateLeakedSecrets:
    """Story 044: Rotate Leaked Secrets."""

    def test_old_postgres_password_rejected(self):
        """AC: Old postgres password no longer authenticates."""
        with pytest.raises(psycopg2.OperationalError, match="password authentication failed"):
            psycopg2.connect(
                host=PG_HOST,
                port=PG_PORT,
                user=PG_USER,
                password=OLD_PG_PASSWORD,
                dbname="sports_data",
                connect_timeout=5,
            )

    def test_new_postgres_password_accepted(self, pg_conn):
        """AC: New postgres password connects successfully."""
        cur = pg_conn.cursor()
        cur.execute("SELECT 1")
        assert cur.fetchone()[0] == 1
        cur.close()

    def test_airflow_scheduler_ready(self, kubectl):
        """AC: Airflow scheduler is Running/Ready after rotation."""
        result = kubectl("get", "pod", "airflow-scheduler-0", "-o", "json")
        assert result.returncode == 0, f"kubectl failed: {result.stderr}"
        pod = json.loads(result.stdout)
        phase = pod["status"]["phase"]
        assert phase == "Running", f"Airflow scheduler phase is '{phase}'"
        ready_conditions = [
            c for c in pod["status"].get("conditions", [])
            if c["type"] == "Ready" and c["status"] == "True"
        ]
        assert ready_conditions, "Airflow scheduler pod is not Ready"

    def test_airflow_webserver_ready(self, kubectl):
        """AC: Airflow webserver is Running/Ready after rotation."""
        result = kubectl("get", "pods", "-l", "component=webserver", "-o", "json")
        assert result.returncode == 0, f"kubectl failed: {result.stderr}"
        pods = json.loads(result.stdout).get("items", [])
        running = [
            p for p in pods
            if p["status"]["phase"] == "Running"
            and any(
                c["type"] == "Ready" and c["status"] == "True"
                for c in p["status"].get("conditions", [])
            )
        ]
        assert running, "No ready Airflow webserver pods found"

    def test_minio_running(self, kubectl):
        """AC: MinIO pod is Running after password rotation."""
        result = kubectl("get", "pods", "-l", "app=minio", "-o", "json")
        assert result.returncode == 0, f"kubectl failed: {result.stderr}"
        pods = json.loads(result.stdout).get("items", [])
        assert pods, "No MinIO pods found"
        phase = pods[0]["status"]["phase"]
        assert phase == "Running", f"MinIO pod phase is '{phase}'"

    def test_minio_new_password_accepted(self, s3_client):
        """AC: MinIO accessible with new root password."""
        response = s3_client.list_buckets()
        buckets = {b["Name"] for b in response.get("Buckets", [])}
        assert "bronze" in buckets, f"Expected 'bronze' bucket, got: {buckets}"

    def test_postgresql_running(self, kubectl):
        """AC: PostgreSQL pod is still Running after rotation."""
        result = kubectl("get", "pod", "postgresql-0", "-o", "json")
        assert result.returncode == 0, f"kubectl failed: {result.stderr}"
        pod = json.loads(result.stdout)
        phase = pod["status"]["phase"]
        assert phase == "Running", f"PostgreSQL pod phase is '{phase}'"
