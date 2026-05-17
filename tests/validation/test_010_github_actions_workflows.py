"""Validation tests for Story 010 – GitHub Actions CI/CD Workflows.

All tests verify live pipeline state via the gh CLI. Story is not done
until CI passes on main, the deploy workflow runs end-to-end, and the
self-hosted Pi runner is registered and online.
"""

import json
import subprocess

import pytest

pytestmark = pytest.mark.k3s


def _gh(*args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(["gh", *args], capture_output=True, text=True, timeout=timeout)


def _require_gh() -> None:
    result = _gh("auth", "status")
    if result.returncode != 0:
        pytest.skip("gh CLI not authenticated — set GITHUB_TOKEN and run gh auth login")


class TestGitHubActionsWorkflows:
    """Story 010: GitHub Actions CI/CD Workflows."""

    def test_ci_workflow_passes_on_main(self):
        """AC: CI workflow runs on main and lint/test/dbt all pass."""
        _require_gh()
        result = _gh(
            "run", "list",
            "--workflow", "ci.yml",
            "--branch", "main",
            "--limit", "1",
            "--json", "conclusion,status",
        )
        assert result.returncode == 0, f"gh run list failed: {result.stderr}"
        runs = json.loads(result.stdout)
        assert runs, "No CI workflow runs found — push to main to trigger CI"
        latest = runs[0]
        assert latest["conclusion"] == "success", (
            f"Latest CI run concluded '{latest['conclusion']}', expected 'success'"
        )

    def test_deploy_workflow_succeeded(self):
        """AC: terraform plan and apply jobs complete successfully in the deploy workflow."""
        _require_gh()
        result = _gh(
            "run", "list",
            "--workflow", "deploy.yml",
            "--branch", "main",
            "--limit", "1",
            "--json", "conclusion,status",
        )
        assert result.returncode == 0, f"gh run list failed: {result.stderr}"
        runs = json.loads(result.stdout)
        assert runs, "No deploy workflow runs found — push infra/ change to main to trigger deploy"
        latest = runs[0]
        assert latest["conclusion"] == "success", (
            f"Latest deploy run concluded '{latest['conclusion']}', expected 'success'"
        )

    def test_self_hosted_runner_online(self):
        """AC: Self-hosted Pi runner is registered and online."""
        _require_gh()
        result = _gh("api", "repos/:owner/:repo/actions/runners", "--jq", ".runners")
        assert result.returncode == 0, f"gh api runners failed: {result.stderr}"
        runners = json.loads(result.stdout)
        assert runners, "No self-hosted runners registered"
        online = [r for r in runners if r.get("status") == "online"]
        assert online, (
            f"No self-hosted runners online; registered runners: "
            f"{[r['name'] for r in runners]}"
        )

    def test_required_secrets_configured(self):
        """AC: GitHub Secrets POSTGRES_PASSWORD, MINIO_ROOT_PASSWORD, AIRFLOW_FERNET_KEY configured."""
        _require_gh()
        result = _gh("secret", "list", "--json", "name")
        assert result.returncode == 0, f"gh secret list failed: {result.stderr}"
        secrets = {s["name"] for s in json.loads(result.stdout)}
        required = {"POSTGRES_PASSWORD", "MINIO_ROOT_PASSWORD", "AIRFLOW_FERNET_KEY"}
        missing = required - secrets
        assert not missing, f"Missing GitHub Secrets: {missing}"

    def test_images_pushed_to_ghcr(self):
        """AC: ARM64 image matrix build completes and images appear in GHCR."""
        _require_gh()
        result = _gh(
            "api", "orgs/:owner/packages?package_type=container",
            "--jq", "[.[].name]",
        )
        if result.returncode != 0:
            result = _gh(
                "api", "user/packages?package_type=container",
                "--jq", "[.[].name]",
            )
        assert result.returncode == 0, f"gh packages API failed: {result.stderr}"
        packages = json.loads(result.stdout)
        for image in ["airflow", "spark", "mlflow", "ingestion"]:
            matching = [p for p in packages if image in p.lower()]
            assert matching, f"No GHCR package found containing '{image}'"
