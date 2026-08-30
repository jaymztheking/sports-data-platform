"""Tests for FFC ADP ingest (S007, feeding S016/S017's backtestable ADP history).

No network — ``requests.get`` is monkeypatched.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import polars as pl
import pytest

from nfl.config import settings
from nfl.ingest import adp_ffc


def _fake_payload(total_drafts: int = 8162) -> dict[str, Any]:
    return {
        "status": "Success",
        "meta": {
            "type": "PPR",
            "teams": 12,
            "rounds": 15,
            "total_drafts": total_drafts,
            "start_date": "2026-08-23",
            "end_date": "2026-08-30",
        },
        "players": [
            {
                "player_id": 5177,
                "name": "Ja'Marr Chase",
                "position": "WR",
                "team": "CIN",
                "adp": 1.5,
            },
            {
                "player_id": 5670,
                "name": "Bijan Robinson",
                "position": "RB",
                "team": "ATL",
                "adp": 2.1,
            },
        ],
    }


class _FakeResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return self._payload


@pytest.fixture
def fake_get(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    captured: dict[str, Any] = {}

    def _get(url: str, params: dict[str, Any], timeout: float) -> _FakeResponse:
        captured["url"] = url
        captured["params"] = params
        return _FakeResponse(_fake_payload())

    monkeypatch.setattr("nfl.ingest.adp_ffc.requests.get", _get, raising=True)
    return captured


def test_fetch_adp_ffc_adds_metadata(fake_get: dict[str, Any]) -> None:
    out = adp_ffc.fetch_adp_ffc(seasons=[2025])

    assert {"ingested_at", "source"} <= set(out.columns)
    assert out["source"].to_list() == [adp_ffc.SOURCE] * 2
    assert out["ingested_at"].dtype == pl.Datetime
    assert out.select(pl.col("ingested_at").max()).item() <= dt.datetime.now(dt.UTC)


def test_fetch_adp_ffc_preserves_source_columns_and_rows(fake_get: dict[str, Any]) -> None:
    out = adp_ffc.fetch_adp_ffc(seasons=[2025])

    assert {"name", "position", "adp"} <= set(out.columns)
    assert out.height == 2
    assert out["adp"].to_list() == [1.5, 2.1]


def test_fetch_adp_ffc_stamps_the_requested_season(fake_get: dict[str, Any]) -> None:
    out = adp_ffc.fetch_adp_ffc(seasons=[2024])

    assert out["season"].to_list() == [2024, 2024]


def test_fetch_adp_ffc_carries_total_drafts_from_the_response_meta(
    fake_get: dict[str, Any],
) -> None:
    """Draft-count is a confidence signal — a 2022 ADP off 1,633 drafts is noisier
    than a 2026 ADP off 8,000+, and downstream weighting needs to know that."""
    out = adp_ffc.fetch_adp_ffc(seasons=[2025])

    assert out["total_drafts"].to_list() == [8162, 8162]


def test_fetch_adp_ffc_concatenates_multiple_seasons(fake_get: dict[str, Any]) -> None:
    out = adp_ffc.fetch_adp_ffc(seasons=[2024, 2025])

    assert out.height == 4
    assert sorted(out["season"].unique().to_list()) == [2024, 2025]


def test_fetch_adp_ffc_requests_the_configured_teams_and_format(
    fake_get: dict[str, Any],
) -> None:
    adp_ffc.fetch_adp_ffc(seasons=[2025], teams=10, scoring_format="half-ppr")

    assert fake_get["params"]["teams"] == 10
    assert fake_get["params"]["year"] == 2025
    assert "half-ppr" in fake_get["url"]


def test_main_writes_parquet_to_the_configured_data_dir(
    fake_get: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(settings, "data_dir", tmp_path)

    rc = adp_ffc.main(["--season", "2025"])

    target = tmp_path / adp_ffc.FILENAME
    assert rc == 0
    assert target.exists()
    assert pl.read_parquet(target).height == 2


def test_main_defaults_to_the_whole_history_window_plus_the_upcoming_season(
    fake_get: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    monkeypatch.setattr(settings, "history_start_season", 2022)
    monkeypatch.setattr(settings, "default_season", 2025)
    monkeypatch.setattr(settings, "current_season", 2026)

    rc = adp_ffc.main([])

    assert rc == 0
    out = pl.read_parquet(tmp_path / adp_ffc.FILENAME)
    assert sorted(out["season"].unique().to_list()) == [2022, 2023, 2024, 2025, 2026]
