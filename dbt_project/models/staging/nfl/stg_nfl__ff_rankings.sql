-- FantasyPros consensus draft board, narrowed to ONE board.
--
-- The raw feed stacks every variant together (31 page_types x 9 ecr_types: dynasty,
-- best-ball, superflex, rookie, redraft). Without the ecr_type filter a join against
-- player stats fans out several-fold, so the filter is load-bearing, not cosmetic.
--   ro = redraft overall — the board a standard season-long league drafts from.
--
-- Grain: ff_player_id.
--
-- NOT player_join_key x player_position — the 2026 board carries two distinct WRs both
-- named "Isaiah Williams" (ffverse ids 26379 @NYJ and 10977 @FA). Staging keeps both
-- and stays faithful; S005A must resolve the collision at join time rather than have
-- this model silently pick a winner.

with source as (

    select * from {{ source('raw_nfl', 'ff_rankings') }}

),

redraft_overall as (

    select * from source
    where ecr_type = 'ro'

),

renamed as (

    select
        id as ff_player_id,
        player as player_name,
        pos as player_position,
        team,

        -- Mirrors the key built in stg_nfl__player_stats; the two feeds share no id.
        {{ normalize_player_name('player') }} as player_join_key,

        -- Expert consensus rank. This feed has NO adp column — ecr is the cost signal.
        ecr,
        sd as ecr_stddev,
        cast(best as integer) as ecr_best,
        cast(worst as integer) as ecr_worst,
        cast(bye as integer) as bye_week,

        cast(scrape_date as date) as scrape_date,
        ingested_at,
        source as record_source

    from redraft_overall

)

select * from renamed
