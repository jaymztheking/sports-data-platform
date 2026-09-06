"""Ingest FFC ADP: Fantasy Football Calculator API → ``<data_dir>/adp_ffc.parquet``.

Free JSON API, no auth, no key. Unlike ESPN ADP, FFC has real, trustworthy
multi-season history (2022-2026 all verified 2026-08-29) — this is the ADP series
S017 backtests against. It is *not* the market James actually drafts in (that's
ESPN, S016's live-decision ADP source); FFC's role is purely the backtestable
history ESPN can't offer.

One HTTP call per season (the API takes a single ``year``, unlike nflreadpy's
batched ``seasons``), concatenated into one frame.

Run it with::

    python -m nfl.ingest.adp_ffc                    # window + upcoming season
    python -m nfl.ingest.adp_ffc --season 2025      # one season
    python -m nfl.ingest.adp_ffc --teams 10 --format half-ppr

Unit tests mock ``requests.get`` — no network in CI (see tests/ingest/test_adp_ffc.py).
"""

from __future__ import annotations

import argparse
from typing import Any

import polars as pl
import requests

from nfl.config import settings
from nfl.ingest._common import add_metadata, write_parquet

SOURCE = "ffc:adp"
FILENAME = "adp_ffc.parquet"
BASE_URL = "https://fantasyfootballcalculator.com/api/v1/adp/{scoring_format}"


def _fetch_one_season(season: int, teams: int, scoring_format: str) -> pl.DataFrame:
    url = BASE_URL.format(scoring_format=scoring_format)
    params: dict[str, int | str] = {"teams": teams, "year": season, "position": "all"}
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    payload: dict[str, Any] = resp.json()
    df = pl.DataFrame(payload["players"])
    return df.with_columns(
        pl.lit(season).alias("season"),
        pl.lit(payload["meta"]["total_drafts"]).alias("total_drafts"),
    )


def fetch_adp_ffc(seasons: list[int], teams: int = 12, scoring_format: str = "ppr") -> pl.DataFrame:
    """Return FFC ADP for ``seasons`` with metadata columns added."""
    frames = [_fetch_one_season(season, teams, scoring_format) for season in seasons]
    df = pl.concat(frames, how="diagonal_relaxed")
    return add_metadata(df, source=SOURCE)


def main(argv: list[str] | None = None) -> int:
    """Ingest FFC ADP for the season window and write it to Parquet."""
    parser = argparse.ArgumentParser(description="Ingest FFC ADP")
    default_seasons = [*settings.default_seasons, settings.current_season]
    parser.add_argument(
        "--season",
        type=int,
        nargs="+",
        default=default_seasons,
        help=f"season year(s) (default: {default_seasons})",
    )
    parser.add_argument("--teams", type=int, default=12, help="league size (default: 12)")
    parser.add_argument(
        "--format",
        dest="scoring_format",
        default="ppr",
        choices=["ppr", "half-ppr", "standard"],
        help="scoring format (default: ppr, matching this platform's scoring_rules seed)",
    )
    args = parser.parse_args(argv)

    df = fetch_adp_ffc(args.season, teams=args.teams, scoring_format=args.scoring_format)
    path = write_parquet(df, settings.data_dir / FILENAME)
    print(f"{SOURCE} seasons={args.season}: {df.height} rows → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
