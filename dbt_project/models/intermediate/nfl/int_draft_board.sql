-- The draft board, one row per player **per scoring format**.
--
-- Format matters: consensus rank is not scoring-agnostic. The standard board has Jahmyr
-- Gibbs at 1.41 and the PPR board has Ja'Marr Chase at 1.58 -- so ranking a
-- standard-scoring league against PPR consensus is wrong at the very first pick. The
-- previous source (ffverse) only mirrored the PPR page, which is why this moved to
-- FantasyPros directly.
--
-- Dedupe: name+position can still collide (two distinct WRs named "Isaiah Williams"),
-- so a rostered player outranks a free agent, then better ECR wins. Ordering matters --
-- "lowest ecr" alone resolves that pair the wrong way.
--
-- Grain: scoring_format x player_join_key x player_position.

with board as (

    select * from {{ ref('stg_nfl__fp_rankings') }}

),

-- FantasyPros publishes STD / HALF / PPR. A league's own format maps onto one of those:
-- the kiddy league is standard-scoring, so it draws on the STD board. The mapping is in
-- the seed rather than hardcoded, because a league can change rules without a new board
-- existing for it.
settings as (

    select
        scoring_format,
        consensus_format
    from {{ ref('league_settings') }}

),

for_league as (

    select
        s.scoring_format,
        b.fp_player_id,
        b.player_name,
        b.player_position,
        b.player_join_key,
        b.team,
        b.ecr,
        b.ecr_stddev,
        b.ecr_best,
        b.ecr_worst,
        b.bye_week,
        b.board_updated
    from board as b
    inner join settings as s on b.scoring_format = s.consensus_format

),

ranked as (

    select
        *,
        row_number() over (
            partition by scoring_format, player_join_key, player_position
            order by
                case when team = 'FA' then 1 else 0 end,
                ecr
        ) as dedupe_rank
    from for_league

)

select
    scoring_format,
    fp_player_id,
    player_name,
    player_position,
    player_join_key,
    team,
    ecr,
    ecr_stddev,
    ecr_best,
    ecr_worst,
    bye_week,
    board_updated
from ranked
where dedupe_rank = 1
