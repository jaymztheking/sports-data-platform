"""Reference test for weekly ingestion (S003).

Skipped until ``fetch_weekly`` is implemented. It demonstrates the no-network
pattern the ACs require: mock the nflreadpy loader, then assert the transform's
contract (provenance columns + dtypes). Un-skip and extend when you write the core.
"""

from __future__ import annotations

import datetime as dt

import polars as pl
import pytest

pytestmark = pytest.mark.skip(reason="TODO(James): enable when fetch_weekly is implemented (S003)")


def test_fetch_weekly_adds_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    from nfl.ingest import weekly

    fake = pl.DataFrame(
        {"player_id": ["00-1"], "season": [2025], "week": [1], "fantasy_points": [12.3]}
    )

    # Patch the loader James calls inside fetch_weekly (adjust the attribute name
    # to whatever nflreadpy function the implementation uses).
    monkeypatch.setattr("nflreadpy.load_player_stats", lambda *a, **k: fake, raising=False)

    out = weekly.fetch_weekly(season=2025)

    assert {"ingested_at", "source"} <= set(out.columns)
    assert out["source"].to_list() == [weekly.SOURCE]
    assert out["ingested_at"].dtype == pl.Datetime
    assert out.select(pl.col("ingested_at").max()).item() <= dt.datetime.now(dt.UTC)
