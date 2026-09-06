"""Ingest FantasyPros consensus rankings, one board per scoring format.

Why this exists alongside ``ff_rankings`` (the ffverse mirror):

1. **ffverse only carries the PPR board.** Its `redraft-overall` rows come from
   ``/nfl/rankings/ppr-cheatsheets.php``, and the feed has no standard or half-PPR page
   at all. Using it for a standard-scoring league compares production under one rulebook
   to consensus under another -- and the mismatch reaches the very top: the STD consensus
   #1 is Jahmyr Gibbs, the PPR #1 is Ja'Marr Chase.
2. **It is fresher.** FantasyPros publishes daily; the ffverse mirror lagged it by two
   days when checked, which matters for in-season use.

The rankings live in a ``var ecrData = {...}`` blob on each public page. ``rank_ave`` is
the averaged expert rank -- the direct analogue of ffverse's ``ecr``. Do **not** use
``rank_ecr``: that is an integer ordinal on a different scale.

Run it with::

    python -m nfl.ingest.fp_rankings
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.request
from typing import Any

import polars as pl

from nfl.config import settings
from nfl.ingest._common import add_metadata, write_parquet

SOURCE = "fantasypros:rankings"
FILENAME = "fp_rankings.parquet"
BASE = "https://www.fantasypros.com/nfl/rankings/{page}.php"
UA = "Mozilla/5.0 (compatible; sports-data-platform/1.0)"

# scoring key -> FantasyPros page. The keys match `scoring_format` in the dbt seed.
PAGES = {
    "standard": "consensus-cheatsheets",
    "half_ppr": "half-point-ppr-cheatsheets",
    "ppr": "ppr-cheatsheets",
}

_ECR_RE = re.compile(r"var ecrData = (\{.*?\});\s*\n", re.S)


def _fetch_page(page: str) -> dict[str, Any]:
    req = urllib.request.Request(BASE.format(page=page), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:  # noqa: S310
        html = resp.read().decode("utf-8", errors="replace")
    match = _ECR_RE.search(html) or re.search(r"var ecrData = (\{.*\})", html)
    if match is None:
        raise RuntimeError(f"no ecrData block on {page} — the page layout likely changed")
    parsed: dict[str, Any] = json.loads(match.group(1))
    return parsed


def fetch_fp_rankings() -> pl.DataFrame:
    """Return every scoring format's consensus board, stacked, with metadata columns."""
    frames = []
    for scoring, page in PAGES.items():
        blob = _fetch_page(page)
        players = blob.get("players", [])
        if not players:
            raise RuntimeError(f"{page} returned no players")
        frames.append(
            pl.DataFrame(
                {
                    "scoring_format": [scoring] * len(players),
                    "fp_scoring": [blob.get("scoring")] * len(players),
                    "last_updated": [blob.get("last_updated")] * len(players),
                    "player_name": [p.get("player_name") for p in players],
                    "player_position": [p.get("player_position_id") for p in players],
                    "team": [p.get("player_team_id") for p in players],
                    # rank_ave is the averaged expert rank; rank_ecr is an integer ordinal
                    # on a different scale and must not be substituted for it.
                    "rank_ave": [_f(p.get("rank_ave")) for p in players],
                    "rank_std": [_f(p.get("rank_std")) for p in players],
                    "rank_min": [_f(p.get("rank_min")) for p in players],
                    "rank_max": [_f(p.get("rank_max")) for p in players],
                    "bye_week": [_i(p.get("player_bye_week")) for p in players],
                    "fp_player_id": [p.get("player_id") for p in players],
                }
            )
        )
    df = pl.concat(frames)
    df = add_metadata(df, source=SOURCE)
    return df


def _f(v: Any) -> float | None:
    """FantasyPros returns these as strings, and blanks for unranked players."""
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _i(v: Any) -> int | None:
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def main(argv: list[str] | None = None) -> int:
    """Ingest every scoring format's consensus board and write it to Parquet."""
    parser = argparse.ArgumentParser(description="Ingest FantasyPros consensus rankings")
    parser.parse_args(argv)

    df = fetch_fp_rankings()
    path = write_parquet(df, settings.data_dir / FILENAME)
    formats = df["scoring_format"].unique().to_list()
    print(f"{SOURCE}: {df.height} rows across {sorted(formats)} → {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
