"""Validation tests for Story 002 – Terraform Foundation.

Verifies that Terraform provider configs and variable definitions exist
so that K3s infrastructure can be managed declaratively.
"""

import os
import re

import pytest

from .conftest import TERRAFORM_DIR

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _tf_file(name: str) -> str:
    return os.path.join(TERRAFORM_DIR, name)


def _read(name: str) -> str:
    path = _tf_file(name)
    assert os.path.isfile(path), f"{path} does not exist"
    with open(path) as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# Tests — each maps to one acceptance criterion
# ---------------------------------------------------------------------------


class TestTerraformFoundation:
    """Story 002: Terraform Foundation."""

    def test_versions_tf_pins_providers(self):
        """AC: versions.tf pins Helm and Kubernetes provider versions."""
        content = _read("versions.tf")
        assert "helm" in content.lower(), "Helm provider not found in versions.tf"
        assert "kubernetes" in content.lower(), "Kubernetes provider not found in versions.tf"
        # Should have version constraints
        assert "version" in content, "No version pinning found in versions.tf"

    def test_main_tf_configures_providers(self):
        """AC: main.tf configures Helm and Kubernetes providers with kubeconfig."""
        content = _read("main.tf")
        assert "provider" in content, "No provider block in main.tf"
        assert "kubeconfig" in content.lower() or "config_path" in content, (
            "kubeconfig reference not found in main.tf"
        )

    def test_main_tf_creates_namespace(self):
        """AC: main.tf creates the data-platform namespace."""
        content = _read("main.tf")
        assert "kubernetes_namespace" in content or "data-platform" in content, (
            "Namespace resource not found in main.tf"
        )

    def test_variables_tf_defines_inputs(self):
        """AC: variables.tf defines all configurable inputs."""
        content = _read("variables.tf")
        expected_vars = ["kubeconfig", "namespace"]
        for var in expected_vars:
            assert var in content.lower(), f"Variable '{var}' not found in variables.tf"

    def test_sensitive_variables_marked(self):
        """AC: Sensitive variables marked with sensitive = true."""
        content = _read("variables.tf")
        assert "sensitive" in content, "No sensitive markers found in variables.tf"
        assert "true" in content, "No sensitive = true found in variables.tf"

    def test_outputs_tf_exposes_service_urls(self):
        """AC: outputs.tf exposes service URLs (Airflow, MinIO, MLflow)."""
        content = _read("outputs.tf")
        for service in ["airflow", "minio", "mlflow"]:
            assert service in content.lower(), f"{service} URL not exposed in outputs.tf"
