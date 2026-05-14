select
    player_id_fg,
    player_name,
    team,
    season,
    wins,
    losses,
    era,
    games,
    games_started,
    innings_pitched,
    strikeouts,
    walks,
    hits_allowed,
    home_runs_allowed,
    whip,
    k_per_9,
    bb_per_9,
    fip,
    war
from {{ ref('stg_mlb__pitching') }}
where innings_pitched > 0
