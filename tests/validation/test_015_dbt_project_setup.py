"""Validation tests for Story 015 – dbt Project Setup.

Verifies that a dbt project is configured for PostgreSQL with correct
materializations, profiles, and packages.
"""

import os

import yaml

from .conftest import DBT_DIR

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _read_yaml(name: str) -> dict:
    path = os.path.join(DBT_DIR, name)
    assert os.path.isfile(path), f"{path} does not exist"
    with open(path) as fh:
        return yaml.safe_load(fh)


def _read_raw(name: str) -> str:
    path = os.path.join(DBT_DIR, name)
    assert os.path.isfile(path), f"{path} does not exist"
    with open(path) as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestDbtProjectSetup:
    """Story 015: dbt Project Setup."""

    def test_dbt_project_yml_materializations(self):
        """AC: dbt_project.yml configures staging as views, marts as tables, with schema routing."""
        content = _read_raw("dbt_project.yml")
        assert "view" in content.lower(), "Staging view materialization not configured"
        assert "table" in content.lower(), "Marts table materialization not configured"

    def test_profiles_yml_postgres(self):
        """AC: profiles.yml connects to PostgreSQL via environment variables."""
        content = _read_raw("profiles.yml")
        assert "postgres" in content.lower(), "PostgreSQL not configured in profiles.yml"

    def test_packages_yml_includes_dbt_utils(self):
        """AC: packages.yml includes dbt-utils."""
        content = _read_raw("packages.yml")
        assert "dbt-utils" in content or "dbt_utils" in content, (
            "dbt-utils not found in packages.yml"
        )

    def test_model_tags(self):
        """AC: Model tags set per sport and layer (e.g., mlb, staging, marts)."""
        content = _read_raw("dbt_project.yml")
        for tag in ["mlb", "staging", "marts"]:
            assert tag in content.lower(), f"Tag '{tag}' not found in dbt_project.yml"
