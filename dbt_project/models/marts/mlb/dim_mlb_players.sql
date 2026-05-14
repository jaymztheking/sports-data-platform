with batters as (
    select distinct
        player_id_fg,
        player_name,
        team,
        'batter' as player_type,
        season
    from {{ ref('stg_mlb__batting') }}
),

pitchers as (
    select distinct
        player_id_fg,
        player_name,
        team,
        'pitcher' as player_type,
        season
    from {{ ref('stg_mlb__pitching') }}
),

combined as (
    select * from batters
    union all
    select * from pitchers
),

deduped as (
    select
        player_id_fg,
        player_name,
        team,
        player_type,
        season,
        row_number() over (
            partition by player_id_fg, season
            order by player_type
        ) as rn
    from combined
)

select
    player_id_fg,
    player_name,
    team,
    player_type,
    season
from deduped
where rn = 1
