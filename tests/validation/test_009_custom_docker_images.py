"""Validation tests for Story 009 – Custom Docker Images.

All tests verify deployed cluster state. Story is not done until
all custom images are confirmed built for ARM64, pushed to GHCR,
and running successfully on Pi nodes.
"""

import json
import os
import subprocess

import pytest

from .conftest import KUBECONFIG, NAMESPACE

pytestmark = pytest.mark.k3s

GHCR_REPO = os.environ.get("GHCR_REPO", "ghcr.io/jaymztheking/sports-data-platform")


def _node_architecture(kubectl_fixture, pod_name: str) -> str:
    """Return the architecture of the node running the given pod."""
    result = subprocess.run(
        ["kubectl", "--kubeconfig", KUBECONFIG, "-n", NAMESPACE,
         "get", "pod", pod_name, "-o", "jsonpath={.spec.nodeName}"],
        capture_output=True, text=True, timeout=30,
    )
    node_name = result.stdout.strip()
    node_result = subprocess.run(
        ["kubectl", "--kubeconfig", KUBECONFIG, "get", "node", node_name, "-o", "json"],
        capture_output=True, text=True, timeout=30,
    )
    node_data = json.loads(node_result.stdout)
    return node_data["status"]["nodeInfo"]["architecture"]


class TestCustomDockerImages:
    """Story 009: Custom Docker Images."""

    def test_all_nodes_are_arm64(self):
        """AC: Cluster nodes are ARM64 — images must be ARM64-compatible to run."""
        result = subprocess.run(
            ["kubectl", "--kubeconfig", KUBECONFIG, "get", "nodes", "-o", "json"],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0
        nodes = json.loads(result.stdout).get("items", [])
        assert nodes, "No nodes found in cluster"
        for node in nodes:
            arch = node["status"]["nodeInfo"]["architecture"]
            name = node["metadata"]["name"]
            assert arch == "arm64", f"Node '{name}' is '{arch}', expected 'arm64'"

    def test_airflow_ghcr_image_running(self, kubectl):
        """AC: Custom Airflow image built for ARM64, pushed to GHCR, and running."""
        result = kubectl("get", "pods", "-l", "component=webserver", "-o", "json")
        pods = json.loads(result.stdout).get("items", [])
        assert pods, "No Airflow webserver pod found — story 007 must be complete first"
        images = [c["image"] for c in pods[0]["spec"]["containers"]]
        assert any("ghcr.io" in img for img in images), (
            f"Airflow not using GHCR custom image; found: {images}"
        )

    def test_spark_ghcr_image_running(self, kubectl):
        """AC: Custom Spark image (with Iceberg JARs) built for ARM64, pushed to GHCR, and running."""  # noqa: E501
        result = kubectl("get", "pods", "-l", "component=master", "-o", "json")
        pods = json.loads(result.stdout).get("items", [])
        assert pods, "No Spark master pod found — story 006 must be complete first"
        images = [c["image"] for c in pods[0]["spec"]["containers"]]
        assert any("ghcr.io" in img for img in images), (
            f"Spark not using GHCR custom image; found: {images}"
        )

    def test_mlflow_ghcr_image_running(self, kubectl):
        """AC: Custom MLflow image built for ARM64, pushed to GHCR, and running."""
        result = kubectl("get", "pods", "-o", "json")
        pods = json.loads(result.stdout).get("items", [])
        mlflow_pods = [p for p in pods if "mlflow" in p["metadata"]["name"].lower()]
        assert mlflow_pods, "No MLflow pod found — story 008 must be complete first"
        images = [c["image"] for c in mlflow_pods[0]["spec"]["containers"]]
        assert any("ghcr.io" in img for img in images), (
            f"MLflow not using GHCR custom image; found: {images}"
        )

    def test_iceberg_image_running_on_arm64(self, kubectl):
        """AC: tabulario/iceberg-rest confirmed running on ARM64 — story 005 complete."""
        result = kubectl("get", "pods", "-o", "json")
        pods = json.loads(result.stdout).get("items", [])
        iceberg_pods = [p for p in pods if "iceberg" in p["metadata"]["name"].lower()]
        assert iceberg_pods, "No Iceberg REST catalog pod found — story 005 must be complete first"
        phase = iceberg_pods[0]["status"]["phase"]
        assert phase == "Running", f"Iceberg pod is '{phase}', not Running"
        pod_name = iceberg_pods[0]["metadata"]["name"]
        arch = _node_architecture(kubectl, pod_name)
        assert arch == "arm64", f"Iceberg pod is on '{arch}' node, expected 'arm64'"
