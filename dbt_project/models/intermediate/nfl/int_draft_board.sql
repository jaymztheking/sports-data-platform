-- The draft board, reduced to one row per player.
--
-- stg_nfl__ff_rankings is faithful to the feed and grains on ff_player_id, which means
-- player_join_key + position can repeat: the 2026 board carries two distinct WRs named
-- "Isaiah Williams" (ffverse 26379 @NYJ, 10977 @FA). Joining that to production without
-- deduping would fan the mart out and double-count a player.
--
-- The tie-break is deliberate and ordered: a rostered player outranks a free agent
-- (a FA is not the person you are drafting), then better ECR wins. Picking "lowest ecr"
-- alone would resolve Isaiah Williams the wrong way — the FA sits at 297.5, ahead of the
-- rostered player's 301.6.
--
-- Grain: player_join_key x player_position.

with board as (

    select * from {{ ref('stg_nfl__ff_rankings') }}

),

ranked as (

    select
        *,
        row_number() over (
            partition by player_join_key, player_position
            order by
                case when team = 'FA' then 1 else 0 end,
                ecr
        ) as dedupe_rank
    from board

)

select
    ff_player_id,
    player_name,
    player_position,
    player_join_key,
    team,
    ecr,
    ecr_stddev,
    ecr_best,
    ecr_worst,
    bye_week,
    scrape_date
from ranked
where dedupe_rank = 1
