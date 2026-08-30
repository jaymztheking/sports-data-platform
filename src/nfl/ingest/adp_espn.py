"""Ingest ESPN ADP: ESPN fantasy API → ``<data_dir>/adp_espn.parquet``.

Free JSON, no auth. ``player.ownership.averageDraftPosition`` is **the market
James actually drafts in** — the live-decision ADP source S016 measures ECR
against. Unlike FFC (S007's ``adp_ffc.py``), ESPN's own historical pull is
unreliable: 2025 returns a constant ``170.0`` for every player instead of
erroring. So this module **only ever pulls the current season** by default, and
``fetch_adp_espn`` refuses to return data shaped like that failure mode.

ESPN's response is deeply nested (per-player stats/projections/rankings
this ingest doesn't need); ``fetch_adp_espn`` flattens it to just the identity +
ADP fields S016 needs, rather than landing the raw payload faithfully the way the
nflreadpy-backed modules do — there is no tabular "faithful" shape here to land.

Run it with::

    python -m nfl.ingest.adp_espn                    # current season only
    python -m nfl.ingest.adp_espn --season 2026 --limit 800

Unit tests mock ``requests.get`` — no network in CI (see tests/ingest/test_adp_espn.py).
"""

from __future__ import annotations

import argparse
import json
from typing import Any

import polars as pl
import requests

from nfl.config import settings
from nfl.ingest._common import add_metadata, write_parquet

SOURCE = "espn:adp"
FILENAME = "adp_espn.parquet"
BASE_URL = "https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/{season}/segments/0/leaguedefaults/3"
DEFAULT_LIMIT = 600


def _flatten(payload: dict[str, Any]) -> pl.DataFrame:
    rows = []
    for entry in payload["players"]:
        player = entry["player"]
        ownership = player.get("ownership") or {}
        rows.append(
            {
                "espn_player_id": player["id"],
                "player_name": player["fullName"],
                "position_id": player["defaultPositionId"],
                "pro_team_id": player["proTeamId"],
                "adp": ownership.get("averageDraftPosition"),
                "pct_owned": ownership.get("percentOwned"),
                "pct_started": ownership.get("percentStarted"),
            }
        )
    return pl.DataFrame(rows)


def _assert_not_sentinel(df: pl.DataFrame) -> None:
    """Reject the known failure mode: every ``adp`` value identical (e.g. ESPN's
    2025-history constant ``170.0``) rather than silently ingesting it as real."""
    non_null = df["adp"].drop_nulls()
    if non_null.len() >= 3 and non_null.n_unique() <= 1:
        raise ValueError(
            f"ESPN ADP looks like the known sentinel failure mode: all "
            f"{non_null.len()} non-null values are constant ({non_null[0]}). "
            "Refusing to ingest — ESPN's historical ADP pull is known unreliable."
        )


def fetch_adp_espn(season: int, limit: int = DEFAULT_LIMIT) -> pl.DataFrame:
    """Return flattened ESPN ADP for ``season`` with metadata columns added."""
    url = BASE_URL.format(season=season)
    headers = {
        "Accept": "application/json",
        "X-Fantasy-Filter": json.dumps(
            {
                "players": {
                    "limit": limit,
                    "sortDraftRanks": {"sortPriority": 1, "sortAsc": True, "value": "STANDARD"},
                }
            }
        ),
    }
    resp = requests.get(url, params={"view": "kona_player_info"}, headers=headers, timeout=30)
    resp.raise_for_status()
    df = _flatten(resp.json())
    _assert_not_sentinel(df)
    df = df.with_columns(pl.lit(season).alias("season"))
    return add_metadata(df, source=SOURCE)


def main(argv: list[str] | None = None) -> int:
    """Ingest the current season's ESPN ADP and write it to Parquet."""
    parser = argparse.ArgumentParser(description="Ingest ESPN ADP")
    parser.add_argument(
        "--season",
        type=int,
        default=settings.current_season,
        help=f"season year (default: {settings.current_season}) — historical pulls are "
        "not recommended, see module docstring",
    )
    parser.add_argument(
        "--limit", type=int, default=DEFAULT_LIMIT, help=f"player limit (default: {DEFAULT_LIMIT})"
    )
    args = parser.parse_args(argv)

    df = fetch_adp_espn(args.season, limit=args.limit)
    path = write_parquet(df, settings.data_dir / FILENAME)
    print(f"{SOURCE} season={args.season}: {df.height} rows → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
