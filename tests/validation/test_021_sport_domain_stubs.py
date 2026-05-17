"""Validation tests for Story 021 – Sport Domain Package Stubs.

Verifies that package stubs exist for NFL, NBA, and NHL domains so that
the project structure is ready for expansion.
"""

import os

import pytest

from .conftest import SRC_DIR

DOMAINS_DIR = os.path.join(SRC_DIR, "domains")

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestSportDomainStubs:
    """Story 021: Sport Domain Package Stubs."""

    def test_nfl_stub(self):
        """AC: src/domains/nfl/ with __init__.py and ingestion/__init__.py."""
        nfl_init = os.path.join(DOMAINS_DIR, "nfl", "__init__.py")
        nfl_ingest_init = os.path.join(DOMAINS_DIR, "nfl", "ingestion", "__init__.py")
        assert os.path.isfile(nfl_init), f"{nfl_init} does not exist"
        assert os.path.isfile(nfl_ingest_init), f"{nfl_ingest_init} does not exist"

    def test_nba_stub(self):
        """AC: src/domains/nba/ with __init__.py and ingestion/__init__.py."""
        nba_init = os.path.join(DOMAINS_DIR, "nba", "__init__.py")
        nba_ingest_init = os.path.join(DOMAINS_DIR, "nba", "ingestion", "__init__.py")
        assert os.path.isfile(nba_init), f"{nba_init} does not exist"
        assert os.path.isfile(nba_ingest_init), f"{nba_ingest_init} does not exist"

    def test_nhl_stub(self):
        """AC: src/domains/nhl/ with __init__.py and ingestion/__init__.py."""
        nhl_init = os.path.join(DOMAINS_DIR, "nhl", "__init__.py")
        nhl_ingest_init = os.path.join(DOMAINS_DIR, "nhl", "ingestion", "__init__.py")
        assert os.path.isfile(nhl_init), f"{nhl_init} does not exist"
        assert os.path.isfile(nhl_ingest_init), f"{nhl_ingest_init} does not exist"
