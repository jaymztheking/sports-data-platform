"""Tests for ESPN ADP ingest (S007, feeding S016's live-market ADP feature).

No network — ``requests.get`` is monkeypatched.

ESPN ADP is the market James actually drafts in, but its historical pull is known
unreliable: the 2025 season returns a constant ``170.0`` sentinel for every player
instead of erroring. `fetch_adp_espn` must reject that shape rather than silently
ingesting it — see `test_fetch_adp_espn_rejects_a_constant_adp_column`.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

import polars as pl
import pytest

from nfl.config import settings
from nfl.ingest import adp_espn


def _player(pid: int, name: str, pos: int, team: int, adp: float) -> dict[str, Any]:
    return {
        "player": {
            "id": pid,
            "fullName": name,
            "defaultPositionId": pos,
            "proTeamId": team,
            "ownership": {
                "averageDraftPosition": adp,
                "percentOwned": 99.9,
                "percentStarted": 95.0,
            },
        }
    }


def _healthy_payload() -> dict[str, Any]:
    return {
        "players": [
            _player(4429795, "Jahmyr Gibbs", 2, 8, 1.38),
            _player(4432773, "Bijan Robinson", 2, 1, 2.42),
            _player(4426515, "Ja'Marr Chase", 3, 4, 4.19),
        ]
    }


def _sentinel_payload() -> dict[str, Any]:
    return {
        "players": [
            _player(4426515, "Ja'Marr Chase", 3, 4, 170.0),
            _player(4432773, "Bijan Robinson", 2, 1, 170.0),
            _player(4241389, "Justin Jefferson", 3, 16, 170.0),
            _player(4239996, "Saquon Barkley", 2, 21, 170.0),
        ]
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
    captured: dict[str, Any] = {"payload": _healthy_payload()}

    def _get(
        url: str, params: dict[str, Any], headers: dict[str, Any], timeout: float
    ) -> _FakeResponse:
        captured["url"] = url
        captured["params"] = params
        captured["headers"] = headers
        return _FakeResponse(captured["payload"])

    monkeypatch.setattr("nfl.ingest.adp_espn.requests.get", _get, raising=True)
    return captured


def test_fetch_adp_espn_adds_metadata(fake_get: dict[str, Any]) -> None:
    out = adp_espn.fetch_adp_espn(season=2026)

    assert {"ingested_at", "source"} <= set(out.columns)
    assert out["source"].to_list() == [adp_espn.SOURCE] * 3
    assert out["ingested_at"].dtype == pl.Datetime
    assert out.select(pl.col("ingested_at").max()).item() <= dt.datetime.now(dt.UTC)


def test_fetch_adp_espn_flattens_the_expected_fields(fake_get: dict[str, Any]) -> None:
    out = adp_espn.fetch_adp_espn(season=2026)

    assert {"espn_player_id", "player_name", "position_id", "pro_team_id", "adp"} <= set(
        out.columns
    )
    assert out.sort("adp")["player_name"].to_list() == [
        "Jahmyr Gibbs",
        "Bijan Robinson",
        "Ja'Marr Chase",
    ]


def test_fetch_adp_espn_stamps_the_requested_season(fake_get: dict[str, Any]) -> None:
    out = adp_espn.fetch_adp_espn(season=2026)

    assert out["season"].to_list() == [2026] * 3


def test_fetch_adp_espn_requests_the_configured_season_and_limit(
    fake_get: dict[str, Any],
) -> None:
    adp_espn.fetch_adp_espn(season=2026, limit=500)

    assert str(2026) in fake_get["url"]
    import json

    filt = json.loads(fake_get["headers"]["X-Fantasy-Filter"])
    assert filt["players"]["limit"] == 500


def test_fetch_adp_espn_rejects_a_constant_adp_column(fake_get: dict[str, Any]) -> None:
    """The known 2025-history failure mode: ESPN returns 170.0 for every player
    instead of erroring. Ingest must not silently write that as if it were real."""
    fake_get["payload"] = _sentinel_payload()

    with pytest.raises(ValueError, match="constant"):
        adp_espn.fetch_adp_espn(season=2025)


def test_main_writes_parquet_to_the_configured_data_dir(
    fake_get: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(settings, "data_dir", tmp_path)

    rc = adp_espn.main([])

    target = tmp_path / adp_espn.FILENAME
    assert rc == 0
    assert target.exists()
    assert pl.read_parquet(target).height == 3


def test_main_defaults_to_the_current_season_only(
    fake_get: dict[str, Any], monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """No historical pull is attempted by default — ESPN history is untrustworthy."""
    monkeypatch.setattr(settings, "data_dir", tmp_path)
    monkeypatch.setattr(settings, "current_season", 2026)

    adp_espn.main([])

    assert str(2026) in fake_get["url"]
