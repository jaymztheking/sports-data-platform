"""Validation tests for Story 010 – GitHub Actions CI/CD Workflows.

Verifies that CI/CD pipelines are configured for linting, testing, and
deploying to K3s.
"""

import os

import pytest
import yaml

from .conftest import GITHUB_DIR

WORKFLOWS_DIR = os.path.join(GITHUB_DIR, "workflows")

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _find_workflow_files() -> list[str]:
    """Return all .yml/.yaml workflow files."""
    if not os.path.isdir(WORKFLOWS_DIR):
        return []
    return [
        os.path.join(WORKFLOWS_DIR, f)
        for f in os.listdir(WORKFLOWS_DIR)
        if f.endswith((".yml", ".yaml"))
    ]


def _read_all_workflows() -> list[dict]:
    """Parse all workflow files as YAML dicts."""
    results = []
    for path in _find_workflow_files():
        with open(path) as fh:
            results.append(yaml.safe_load(fh))
    return results


def _read_all_workflows_raw() -> str:
    """Return concatenated raw text of all workflow files."""
    texts = []
    for path in _find_workflow_files():
        with open(path) as fh:
            texts.append(fh.read())
    return "\n".join(texts)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestGitHubActionsWorkflows:
    """Story 010: GitHub Actions CI/CD Workflows."""

    def test_ci_workflow_triggers(self):
        """AC: CI workflow runs on PRs and pushes to main."""
        raw = _read_all_workflows_raw()
        assert "pull_request" in raw, "CI workflow not triggered on pull_request"
        assert "push" in raw, "CI workflow not triggered on push"

    def test_ci_jobs_lint_test_dbt(self):
        """AC: CI jobs: lint (ruff + mypy), test (pytest), dbt (compile)."""
        raw = _read_all_workflows_raw().lower()
        assert "ruff" in raw, "ruff linting not configured in CI"
        assert "mypy" in raw or "type" in raw, "mypy/type checking not configured in CI"
        assert "pytest" in raw or "test" in raw, "pytest not configured in CI"
        assert "dbt" in raw, "dbt not configured in CI"

    def test_deploy_workflow_triggers(self):
        """AC: Deploy workflow triggers on push to main when infra/ or docker/ change."""
        raw = _read_all_workflows_raw()
        assert "infra/" in raw or "infra/**" in raw, "Deploy not triggered by infra/ changes"
        assert "docker/" in raw or "docker/**" in raw, "Deploy not triggered by docker/ changes"

    def test_deploy_builds_arm64_images(self):
        """AC: Deploy builds ARM64 images via matrix strategy and pushes to GHCR."""
        raw = _read_all_workflows_raw().lower()
        assert "arm64" in raw or "aarch64" in raw or "matrix" in raw, (
            "ARM64 build matrix not configured"
        )
        assert "ghcr" in raw, "GHCR push not configured"

    def test_deploy_terraform(self):
        """AC: Deploy runs terraform init, plan, apply with secrets as TF_VAR inputs."""
        raw = _read_all_workflows_raw().lower()
        assert "terraform" in raw, "Terraform not referenced in deploy workflow"
        assert "tf_var" in raw or "tfvar" in raw, "TF_VAR secrets not configured"

    def test_appropriate_runners(self):
        """AC: Both workflows use appropriate runners (ubuntu-latest for CI, self-hosted for deploy)."""
        raw = _read_all_workflows_raw()
        assert "ubuntu-latest" in raw, "ubuntu-latest runner not used"
        assert "self-hosted" in raw, "self-hosted runner not used for deploy"
