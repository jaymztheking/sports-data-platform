"""Validation tests for Story 018 – MLB Reference Seeds.

Verifies that MLB team reference data is available as a dbt seed file.
"""

import csv
import os

import pytest

from .conftest import DBT_DIR

SEEDS_DIR = os.path.join(DBT_DIR, "seeds")

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestMlbSeeds:
    """Story 018: MLB Reference Seeds."""

    def test_mlb_teams_csv_exists(self):
        """AC: mlb_teams.csv contains all 30 MLB teams with abbreviation, full name, league, and division."""
        # Search for the CSV file under seeds/
        csv_path = None
        for root, _dirs, files in os.walk(SEEDS_DIR):
            for f in files:
                if "mlb_teams" in f and f.endswith(".csv"):
                    csv_path = os.path.join(root, f)
                    break
        assert csv_path is not None, "mlb_teams.csv not found under seeds/"

        with open(csv_path, newline="") as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)

        assert len(rows) == 30, f"Expected 30 MLB teams, found {len(rows)}"

        # Verify expected columns exist
        headers_lower = {h.lower() for h in reader.fieldnames or []}
        assert any("abbr" in h for h in headers_lower), "abbreviation column not found"
        assert any("name" in h for h in headers_lower), "full name column not found"
        assert any("league" in h for h in headers_lower), "league column not found"
        assert any("division" in h for h in headers_lower), "division column not found"
