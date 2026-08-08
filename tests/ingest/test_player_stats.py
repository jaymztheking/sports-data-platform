"""Reference test for player-stats ingestion (S003).

Skipped until ``fetch_player_stats`` is implemented. It demonstrates the no-network
pattern the ACs require: mock the nflreadpy loader, then assert the transform's
contract (provenance columns + dtypes). Un-skip and extend when you write the core.
"""

from __future__ import annotations

import datetime as dt

import polars as pl
import pytest

pytestmark = pytest.mark.skip(
    reason="TODO(James): enable when fetch_player_stats is implemented (S003)"
)


def test_fetch_player_stats_adds_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    from nfl.ingest import player_stats

    fake = pl.DataFrame(
        {"player_id": ["00-1"], "season": [2025], "week": [1], "fantasy_points": [12.3]}
    )

    # Patching the module attribute only works if the implementation calls
    # ``nflreadpy.load_player_stats(...)`` (i.e. ``import nflreadpy as nfl``).
    # A ``from nflreadpy import load_player_stats`` would need the target
    # "nfl.ingest.player_stats.load_player_stats" instead.
    monkeypatch.setattr("nflreadpy.load_player_stats", lambda *a, **k: fake, raising=False)

    out = player_stats.fetch_player_stats(season=2025)

    assert {"ingested_at", "source"} <= set(out.columns)
    assert out["source"].to_list() == [player_stats.SOURCE]
    assert out["ingested_at"].dtype == pl.Datetime
    assert out.select(pl.col("ingested_at").max()).item() <= dt.datetime.now(dt.UTC)
