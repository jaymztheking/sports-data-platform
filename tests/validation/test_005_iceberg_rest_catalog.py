"""Validation tests for Story 005 – Iceberg REST Catalog Deployment.

All tests verify deployed cluster state. Story is not done until
the catalog pod is Running, the HTTP endpoint responds, and it is
confirmed to run on ARM64.
"""

import json
import os
import subprocess

import pytest

from .conftest import KUBECONFIG

pytestmark = pytest.mark.k3s


class TestIcebergRestCatalog:
    """Story 005: Iceberg REST Catalog Deployment."""

    def test_pod_running(self, kubectl):
        """AC: Iceberg REST catalog pod is Running in the data-platform namespace."""
        result = kubectl("get", "pods", "-o", "json")
        assert result.returncode == 0, f"kubectl failed: {result.stderr}"
        pods = json.loads(result.stdout).get("items", [])
        iceberg_pods = [p for p in pods if "iceberg" in p["metadata"]["name"].lower()]
        assert iceberg_pods, "No Iceberg REST catalog pods found"
        phase = iceberg_pods[0]["status"]["phase"]
        assert phase == "Running", f"Iceberg pod phase is '{phase}', expected 'Running'"

    def test_config_endpoint_responds(self, http):
        """AC: Catalog HTTP endpoint responds — GET /v1/config returns 200."""
        url = os.environ.get("ICEBERG_REST_URL", "http://192.168.50.231:30181")
        resp = http.get(f"{url}/v1/config", timeout=10)
        assert resp.status_code == 200, f"Iceberg /v1/config returned {resp.status_code}"

    def test_running_on_arm64_node(self, kubectl):
        """AC: tabulario/iceberg-rest confirmed running on ARM64 Pi node."""
        result = kubectl("get", "pods", "-o", "json")
        pods = json.loads(result.stdout).get("items", [])
        iceberg_pods = [p for p in pods if "iceberg" in p["metadata"]["name"].lower()]
        assert iceberg_pods, "No Iceberg pods found"
        node_name = iceberg_pods[0]["spec"]["nodeName"]
        node_result = subprocess.run(
            ["kubectl", "--kubeconfig", KUBECONFIG, "get", "node", node_name, "-o", "json"],
            capture_output=True, text=True, timeout=30,
        )
        assert node_result.returncode == 0
        node_data = json.loads(node_result.stdout)
        arch = node_data["status"]["nodeInfo"]["architecture"]
        assert arch == "arm64", f"Iceberg pod is on '{arch}' node, expected 'arm64'"

    def test_warehouse_reachable(self, s3_client):
        """AC: S3FileIO warehouse bucket (spark-warehouse) is accessible from catalog perspective."""  # noqa: E501
        response = s3_client.list_buckets()
        bucket_names = {b["Name"] for b in response["Buckets"]}
        assert "spark-warehouse" in bucket_names, "spark-warehouse bucket not found in MinIO"
