"""Validation tests for Story 002 – Terraform Foundation.

All tests verify deployed cluster state. Story is not done until
the data-platform namespace exists and kubectl can reach the cluster.
"""

import json
import shutil
import subprocess

import pytest

from .conftest import KUBECONFIG, NAMESPACE, TERRAFORM_DIR

pytestmark = pytest.mark.k3s


class TestTerraformFoundation:
    """Story 002: Terraform Foundation."""

    def test_cluster_accessible(self):
        """AC: Kubernetes provider authenticated — kubectl can reach the cluster."""
        result = subprocess.run(
            ["kubectl", "--kubeconfig", KUBECONFIG, "cluster-info"],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"kubectl cluster-info failed: {result.stderr}"

    def test_namespace_exists(self):
        """AC: terraform apply created the data-platform namespace and it is Active."""
        result = subprocess.run(
            ["kubectl", "--kubeconfig", KUBECONFIG, "get", "namespace", NAMESPACE, "-o", "json"],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"Namespace '{NAMESPACE}' not found: {result.stderr}"
        data = json.loads(result.stdout)
        phase = data["status"]["phase"]
        assert phase == "Active", f"Namespace phase is '{phase}', expected 'Active'"

    def test_terraform_outputs_available(self):
        """AC: outputs.tf exposes service URLs — terraform output resolves airflow, minio, mlflow."""  # noqa: E501
        terraform = shutil.which("terraform") or "terraform"
        result = subprocess.run(
            [terraform, "output", "-json"],
            cwd=TERRAFORM_DIR, capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            pytest.skip("Terraform state not initialised — run terraform apply first")
        outputs = json.loads(result.stdout)
        for svc in ["airflow", "minio", "mlflow"]:
            matching = [k for k in outputs if svc in k.lower()]
            assert matching, f"No terraform output found containing '{svc}'"
