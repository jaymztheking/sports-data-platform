-- Per-player, per-week stats: the fantasy-relevant subset of the 152 raw columns.
-- Grain: player_id x season x week x season_type.
--
-- Renames only where the raw name is a cross-adapter hazard or genuinely unclear.
-- `position` -> `player_position` because POSITION is a reserved function name in
-- Postgres; leaving it bare would build on DuckDB and fail on prod.

with source as (

    select * from {{ source('raw_nfl', 'player_stats') }}

),

identified as (

    -- 22 rows in the 2025 season carry no player identity at all: null player_id,
    -- null name, null position, 0.0 fantasy points, roughly one per team-week. They
    -- are nflverse placeholders, not player-weeks, and they are the only source of
    -- nulls in the grain key. Dropping them here is what makes the not_null and
    -- uniqueness tests downstream meaningful rather than merely passing.
    select * from source
    where player_id is not null

),

renamed as (

    select
        -- grain
        player_id,
        cast(season as integer) as season,
        cast(week as integer) as week,
        season_type,

        -- identity
        player_name,
        player_display_name,
        position as player_position,
        position_group,
        team,
        opponent_team,

        -- join key for the ffverse draft board, which shares no id with gsis.
        {{ normalize_player_name('player_display_name') }} as player_join_key,

        -- passing
        cast(completions as integer) as completions,
        cast(attempts as integer) as pass_attempts,
        passing_yards,
        cast(passing_tds as integer) as passing_tds,
        cast(passing_interceptions as integer) as interceptions,

        -- rushing
        cast(carries as integer) as carries,
        rushing_yards,
        cast(rushing_tds as integer) as rushing_tds,

        -- receiving
        cast(targets as integer) as targets,
        cast(receptions as integer) as receptions,
        receiving_yards,
        cast(receiving_tds as integer) as receiving_tds,
        receiving_air_yards,
        receiving_yards_after_catch,

        -- opportunity shares (already fractions of team totals)
        target_share,
        air_yards_share,
        wopr,

        -- two-point conversions, worth 2 apiece to the scorer
        cast(passing_2pt_conversions as integer)
        + cast(rushing_2pt_conversions as integer)
        + cast(receiving_2pt_conversions as integer) as two_point_conversions,

        -- return scores; nflverse counts these toward fantasy points
        cast(special_teams_tds as integer) as special_teams_tds,

        -- turnovers that cost fantasy points
        cast(sack_fumbles_lost as integer)
        + cast(rushing_fumbles_lost as integer)
        + cast(receiving_fumbles_lost as integer) as fumbles_lost,

        -- nflverse's own scoring, kept for reconciliation against our seed
        fantasy_points as fantasy_points_std_source,
        fantasy_points_ppr as fantasy_points_ppr_source,

        -- provenance
        ingested_at,
        source as record_source

    from identified

)

select * from renamed
