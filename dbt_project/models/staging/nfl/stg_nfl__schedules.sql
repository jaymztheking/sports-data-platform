-- One row per game (REG + POST). Scores are null until the game is played.
-- Grain: game_id.

with source as (

    select * from {{ source('raw_nfl', 'schedules') }}

),

renamed as (

    select
        game_id,
        cast(season as integer) as season,
        cast(week as integer) as week,
        game_type,

        cast(gameday as date) as game_date,
        weekday,
        gametime,

        home_team,
        away_team,
        cast(home_score as integer) as home_score,
        cast(away_score as integer) as away_score,

        -- nflverse `result` is home_score - away_score; null before kickoff.
        cast(result as integer) as home_margin,
        cast(total as integer) as total_points,
        home_score is not null as is_played,

        -- context that matters for matchup work later (S008+)
        cast(div_game as boolean) as is_division_game,
        roof,
        surface,
        spread_line,
        total_line,
        cast(home_rest as integer) as home_rest_days,
        cast(away_rest as integer) as away_rest_days,

        ingested_at,
        source as record_source

    from source

)

select * from renamed
