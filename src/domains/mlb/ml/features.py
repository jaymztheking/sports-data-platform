"""Feature engineering for MLB ML models."""

import pandas as pd
from sqlalchemy import text

from src.common.postgres import get_engine


def build_pitcher_features() -> str:
    """Build pitcher feature matrix from gold tables. Returns path to saved features."""
    engine = get_engine()

    query = text("""
        select
            player_id_fg,
            player_name,
            season,
            innings_pitched,
            strikeouts,
            walks,
            hits_allowed,
            home_runs_allowed,
            era,
            whip,
            k_per_9,
            bb_per_9,
            fip,
            war,
            lag(strikeouts) over (partition by player_id_fg order by season) as prev_strikeouts,
            lag(k_per_9) over (partition by player_id_fg order by season) as prev_k_per_9,
            lag(innings_pitched) over (partition by player_id_fg order by season) as prev_ip,
            lag(era) over (partition by player_id_fg order by season) as prev_era,
            lag(fip) over (partition by player_id_fg order by season) as prev_fip
        from marts.fct_mlb_pitching_season
        where innings_pitched >= 20
        order by player_id_fg, season
    """)

    df = pd.read_sql(query, engine)
    df = df.dropna(subset=["prev_strikeouts"])

    output_path = "/tmp/pitcher_features.parquet"
    df.to_parquet(output_path, index=False)
    return output_path
