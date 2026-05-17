"""Validation tests for Story 009 – Custom Docker Images.

Verifies that custom Dockerfiles exist for Airflow, Spark, MLflow, and
ingestion with correct configurations for ARM64.
"""

import os

import pytest

from .conftest import DOCKER_DIR

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _docker_path(*parts: str) -> str:
    return os.path.join(DOCKER_DIR, *parts)


def _read_dockerfile(*parts: str) -> str:
    path = _docker_path(*parts)
    assert os.path.isfile(path), f"{path} does not exist"
    with open(path) as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestCustomDockerImages:
    """Story 009: Custom Docker Images."""

    def test_airflow_dockerfile_exists_and_extends(self):
        """AC: Airflow Dockerfile extends official image with project ingestion dependencies via uv."""
        content = _read_dockerfile("airflow", "Dockerfile")
        assert "FROM" in content, "No FROM directive in Airflow Dockerfile"
        assert "airflow" in content.lower(), "Does not extend Airflow image"
        assert "uv" in content.lower(), "uv not used for dependency installation"

    def test_spark_dockerfile_with_iceberg_jars(self):
        """AC: Spark Dockerfile extends bitnami/spark with Iceberg runtime and AWS SDK JARs."""
        content = _read_dockerfile("spark", "Dockerfile")
        assert "FROM" in content, "No FROM directive in Spark Dockerfile"
        assert "spark" in content.lower(), "Does not extend Spark image"
        assert "iceberg" in content.lower(), "Iceberg JARs not referenced"

    def test_spark_defaults_conf(self):
        """AC: spark-defaults.conf pre-configures Iceberg catalog, S3 endpoints, and MinIO credentials."""
        content = _read_dockerfile("spark", "Dockerfile")
        # Check for spark-defaults.conf copy or inline config
        # Also check if the file itself exists
        conf_path = _docker_path("spark", "spark-defaults.conf")
        if os.path.isfile(conf_path):
            with open(conf_path) as fh:
                conf_content = fh.read()
            assert "iceberg" in conf_content.lower(), "Iceberg not configured in spark-defaults.conf"
            assert "s3" in conf_content.lower(), "S3 not configured in spark-defaults.conf"
        else:
            # Config may be inline in Dockerfile
            assert "spark-defaults" in content or "iceberg" in content.lower(), (
                "spark-defaults.conf not found or configured"
            )

    def test_mlflow_dockerfile(self):
        """AC: MLflow Dockerfile installs mlflow, psycopg2-binary, boto3 with shell-form CMD."""
        content = _read_dockerfile("mlflow", "Dockerfile")
        assert "mlflow" in content.lower(), "mlflow not installed"
        assert "psycopg2" in content.lower(), "psycopg2 not installed"
        assert "boto3" in content.lower(), "boto3 not installed"

    def test_ingestion_dockerfile(self):
        """AC: Ingestion Dockerfile installs project with ingestion extras and copies src."""
        content = _read_dockerfile("ingestion", "Dockerfile")
        assert "FROM" in content, "No FROM directive in ingestion Dockerfile"
        assert "COPY" in content, "No COPY directive to copy source"
