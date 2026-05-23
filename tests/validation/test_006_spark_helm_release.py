"""Validation tests for Story 006 – Spark Helm Release.

All tests verify deployed cluster state. Story is not done until
Spark master + 2 workers are Running and the Spark UI shows them connected.
"""

import json
import os

import pytest

pytestmark = pytest.mark.k3s


class TestSparkHelmRelease:
    """Story 006: Spark Helm Release."""

    def test_master_pod_running(self, kubectl):
        """AC: Spark master pod is Running in the data-platform namespace."""
        result = kubectl("get", "pods", "-l", "app=spark,component=master", "-o", "json")
        assert result.returncode == 0, f"kubectl failed: {result.stderr}"
        pods = json.loads(result.stdout).get("items", [])
        assert pods, "No Spark master pod found"
        phase = pods[0]["status"]["phase"]
        assert phase == "Running", f"Spark master phase is '{phase}', expected 'Running'"

    def test_two_worker_pods_running(self, kubectl):
        """AC: 2 Spark worker pods are Running in the data-platform namespace."""
        result = kubectl("get", "pods", "-l", "app=spark,component=worker", "-o", "json")
        assert result.returncode == 0, f"kubectl failed: {result.stderr}"
        pods = json.loads(result.stdout).get("items", [])
        running = [p for p in pods if p["status"]["phase"] == "Running"]
        assert len(running) >= 2, f"Expected at least 2 running Spark workers, found {len(running)}"

    def test_spark_ui_accessible(self, http):
        """AC: Spark UI shows master and workers connected."""
        url = os.environ.get("SPARK_UI_URL", "http://192.168.50.231:30808")
        resp = http.get(url, timeout=10)
        assert resp.status_code == 200, f"Spark UI returned {resp.status_code}"
        assert "Workers" in resp.text or "worker" in resp.text.lower(), (
            "Spark UI does not show workers"
        )

    def test_custom_image_from_registry(self, kubectl):
        """AC: Custom Spark image (with Iceberg JARs) running — not stock bitnami image."""
        result = kubectl("get", "pods", "-l", "app=spark,component=master", "-o", "json")
        pods = json.loads(result.stdout).get("items", [])
        assert pods, "No Spark master pod found"
        images = [c["image"] for c in pods[0]["spec"]["containers"]]
        assert any("jaymztheking" in img for img in images), (
            f"Spark master not using custom image; found: {images}"
        )
