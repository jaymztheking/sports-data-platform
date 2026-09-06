-- FantasyPros consensus rankings, one board per scoring format.
--
-- Supersedes stg_nfl__ff_rankings as the board behind the marts. The ffverse mirror
-- carries only the PPR page, so a standard-scoring league was being ranked against PPR
-- consensus -- a mismatch that reaches the top of the board (STD #1 is Jahmyr Gibbs,
-- PPR #1 is Ja'Marr Chase). This source has all three and is published daily.
--
-- Grain: scoring_format x player_join_key x player_position.

with source as (

    select * from {{ source('raw_nfl', 'fp_rankings') }}

),

skill as (

    -- The mart prices QB/RB/WR/TE only; K and D/ST have no scoring rules here.
    select * from source
    where
        player_position in ('QB', 'RB', 'WR', 'TE')
        and rank_ave is not null

),

renamed as (

    select
        scoring_format,
        {{ normalize_player_name('player_name') }} as player_join_key,
        player_name,
        player_position,
        team,

        -- Averaged expert rank -- the analogue of ffverse's `ecr`. rank_ecr is an integer
        -- ordinal on a different scale and is deliberately not carried.
        rank_ave as ecr,
        rank_std as ecr_stddev,
        rank_min as ecr_best,
        rank_max as ecr_worst,
        cast(bye_week as integer) as bye_week,
        last_updated as board_updated,

        fp_player_id,
        ingested_at,
        source as record_source

    from skill

)

select * from renamed
