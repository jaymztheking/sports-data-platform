"""Validation tests for Story 020 – MLB ML Pipeline Code.

Verifies that a pitcher strikeout projection model exists with MLflow
tracking, feature engineering, and Airflow orchestration.
"""

import os

import pytest

from .conftest import DAGS_DIR, SRC_DIR

MLB_DIR = os.path.join(SRC_DIR, "domains", "mlb")

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _find_module(name: str, search_dir: str) -> str:
    for root, _dirs, files in os.walk(search_dir):
        if name in files:
            return os.path.join(root, name)
    pytest.fail(f"{name} not found under {search_dir}")
    return ""


def _read_module(name: str, search_dir: str = MLB_DIR) -> str:
    path = _find_module(name, search_dir)
    with open(path) as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestMlbMlPipelineCode:
    """Story 020: MLB ML Pipeline Code."""

    def test_features_module(self):
        """AC: features.py queries gold pitching tables, computes lag features, saves to parquet."""
        content = _read_module("features.py")
        assert (
            "lag" in content.lower() or "prev" in content.lower() or "shift" in content.lower()
        ), "Lag feature computation not found in features.py"
        assert "parquet" in content.lower(), "Parquet output not found in features.py"

    def test_pitcher_projections_xgboost(self):
        """AC: pitcher_projections.py trains XGBoost regressor with configurable hyperparameters."""
        content = _read_module("pitcher_projections.py")
        assert "xgboost" in content.lower() or "XGB" in content, (
            "XGBoost not referenced in pitcher_projections.py"
        )

    def test_mlflow_logging(self):
        """AC: Training logs params, metrics (RMSE, MAE, R2), and model artifact to MLflow."""
        content = _read_module("pitcher_projections.py")
        assert "mlflow" in content.lower(), "MLflow not referenced"
        for metric in ["rmse", "mae", "r2"]:
            assert metric in content.lower(), f"Metric '{metric}' not logged"

    def test_evaluate_tags_quality(self):
        """AC: evaluate() tags run quality based on R2 threshold."""
        content = _read_module("pitcher_projections.py")
        assert "evaluate" in content, "evaluate() function not found"
        assert "tag" in content.lower() or "set_tag" in content, (
            "Run quality tagging not found in evaluate()"
        )

    def test_ml_dag_orchestration(self):
        """AC: mlb_ml_dag.py orchestrates build_features -> train -> evaluate in Airflow."""
        content = _read_module("mlb_ml_dag.py", search_dir=DAGS_DIR)
        assert "feature" in content.lower(), "build_features step not found in ML DAG"
        assert "train" in content.lower(), "train step not found in ML DAG"
        assert "evaluate" in content.lower(), "evaluate step not found in ML DAG"
