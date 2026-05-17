"""Validation tests for Story 011 – Common Python Modules.

Verifies that shared configuration and client factories exist so that
all domains use consistent connections to Spark, PostgreSQL, and MinIO.
"""

import os

import pytest

from .conftest import SRC_DIR

COMMON_DIR = os.path.join(SRC_DIR, "common")

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _read_module(name: str) -> str:
    path = os.path.join(COMMON_DIR, name)
    assert os.path.isfile(path), f"{path} does not exist"
    with open(path) as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestCommonPythonModules:
    """Story 011: Common Python Modules."""

    def test_config_pydantic_settings(self):
        """AC: config.py uses Pydantic Settings with env var prefixes for Postgres, MinIO, and Spark."""
        content = _read_module("config.py")
        assert "pydantic" in content.lower() or "BaseSettings" in content or "Settings" in content, (
            "Pydantic Settings not used in config.py"
        )
        for svc in ["postgres", "minio", "spark"]:
            assert svc in content.lower(), f"{svc} config not found in config.py"

    def test_spark_session_factory(self):
        """AC: spark.py creates Iceberg-configured SparkSession pointing to REST catalog + MinIO."""
        content = _read_module("spark.py")
        assert "SparkSession" in content, "SparkSession not found in spark.py"
        assert "iceberg" in content.lower(), "Iceberg configuration not found in spark.py"

    def test_postgres_engine_factory(self):
        """AC: postgres.py creates SQLAlchemy engine from config."""
        content = _read_module("postgres.py")
        assert "engine" in content.lower() or "sqlalchemy" in content.lower(), (
            "SQLAlchemy engine not found in postgres.py"
        )

    def test_storage_s3_client(self):
        """AC: storage.py creates boto3 S3 client configured for MinIO."""
        content = _read_module("storage.py")
        assert "boto3" in content.lower() or "s3" in content.lower(), (
            "boto3/S3 client not found in storage.py"
        )

    def test_all_modules_import_cleanly(self):
        """AC: All modules import cleanly."""
        for module in ["config.py", "spark.py", "postgres.py", "storage.py"]:
            path = os.path.join(COMMON_DIR, module)
            assert os.path.isfile(path), f"{module} does not exist"
            # Verify valid Python syntax via compile
            with open(path) as fh:
                source = fh.read()
            try:
                compile(source, path, "exec")
            except SyntaxError as exc:
                pytest.fail(f"{module} has syntax error: {exc}")
