-- The draft board: one season of a player's production, expressed as rates, ranked
-- within position, and set against what the market is charging for him.
--
-- Grain: player_id x season x scoring_format.
--
-- Read `value_over_ecr` as "spots of value": the player's production rank at his
-- position minus his ECR rank at that position, so +12 means he produced twelve spots
-- better than he is being drafted. Null when a player is not on the board — an honest
-- gap rather than a fabricated zero.
--
-- Filter on `is_draftable` before trusting it. Rank differences are only comparable
-- inside the pool people actually draft; out in the tail the board stops ranking
-- carefully, so a 6 ppg WR who merely played comes out ahead of every real pick.

with weekly as (

    select * from {{ ref('int_player_week_points') }}

),

board as (

    select * from {{ ref('int_draft_board') }}

),

season_totals as (

    select
        player_id,
        season,
        scoring_format,
        max(player_display_name) as player_display_name,
        max(player_position) as player_position,
        max(player_join_key) as player_join_key,
        max(team) as team,

        count(*) as games_played,
        sum(fantasy_points) as fantasy_points_total,
        avg(fantasy_points) as fantasy_points_per_game,

        -- Consistency. A 14 ppg player who alternates 4 and 24 is a different draft
        -- proposition from one who scores 14 every week; the mean alone hides that.
        stddev_samp(fantasy_points) as fantasy_points_stddev,
        percentile_cont(0.25) within group (order by fantasy_points) as fantasy_points_floor,
        percentile_cont(0.75) within group (order by fantasy_points) as fantasy_points_ceiling,

        -- Volume and opportunity
        sum(targets) as targets,
        sum(receptions) as receptions,
        sum(carries) as carries,
        sum(receiving_air_yards) as receiving_air_yards,
        avg(target_share) as target_share_avg,
        avg(air_yards_share) as air_yards_share_avg

    from weekly
    group by player_id, season, scoring_format

),

-- Ranking on per-game points rewards tiny samples: one 30-point game would rank a
-- player above a season-long RB1. Only players with `min_games_for_rank` games are
-- ranked; the rest keep their stats and carry a null rank, which reads as "not enough
-- season to say" rather than as a bad player.
production_ranked as (

    select
        *,
        case
            when games_played >= {{ var('min_games_for_rank') }}
                then row_number() over (
                    partition by season, scoring_format, player_position
                    order by
                        case when games_played >= {{ var('min_games_for_rank') }} then 0 else 1 end,
                        fantasy_points_per_game desc
                )
        end as production_position_rank
    from season_totals

),

-- Replacement level: what you would get from the waiver wire at each position, which
-- is the only thing that makes points comparable ACROSS positions. Raw per-game points
-- are not a draft ranking -- under 6-pt passing TDs the top 15 by points is fifteen
-- quarterbacks, because every startable QB scores a lot. Subtracting replacement is what
-- turns league scoring into a league-specific ordering instead of a column.
settings as (

    select * from {{ ref('league_settings') }}

),

-- Base starters: the players every team must field at a dedicated slot.
qualified as (

    select
        p.*,
        s.teams,
        s.start_qb,
        s.start_rb,
        s.start_wr,
        s.start_te,
        s.start_flex,
        row_number() over (
            partition by p.season, p.scoring_format, p.player_position
            order by p.fantasy_points_per_game desc
        ) as pos_rank
    from production_ranked as p
    inner join settings as s on p.scoring_format = s.scoring_format
    where p.games_played >= {{ var('min_games_for_rank') }}

),

base_starters as (

    select
        *,
        case player_position
            when 'QB' then teams * start_qb
            when 'RB' then teams * start_rb
            when 'WR' then teams * start_wr
            when 'TE' then teams * start_te
        end as dedicated_slots
    from qualified

),

-- FLEX is filled by the best remaining RB/WR/TE, so it deepens whichever positions are
-- actually productive rather than a fixed split.
flex_pool as (

    select
        *,
        row_number() over (
            partition by season, scoring_format
            order by fantasy_points_per_game desc
        ) as flex_rank
    from base_starters
    where
        pos_rank > dedicated_slots
        and player_position in ('RB', 'WR', 'TE')

),

started as (

    select
        season,
        scoring_format,
        player_position,
        fantasy_points_per_game
    from base_starters
    where pos_rank <= dedicated_slots
    union all
    select
        season,
        scoring_format,
        player_position,
        fantasy_points_per_game
    from flex_pool
    where flex_rank <= teams * start_flex

),

-- Replacement = the best player at that position who is NOT started anywhere.
replacement as (

    select
        season,
        scoring_format,
        player_position,
        max(fantasy_points_per_game) as replacement_ppg
    from (
        select
            b.season,
            b.scoring_format,
            b.player_position,
            b.fantasy_points_per_game,
            row_number() over (
                partition by b.season, b.scoring_format, b.player_position
                order by b.fantasy_points_per_game desc
            ) as rn,
            (
                select count(*) from started as st
                where
                    st.season = b.season
                    and st.scoring_format = b.scoring_format
                    and st.player_position = b.player_position
            ) as started_at_pos
        from base_starters as b
    ) as x
    where rn = started_at_pos + 1
    group by season, scoring_format, player_position

),

board_ranked as (

    select
        *,
        row_number() over (
            partition by scoring_format, player_position order by ecr
        ) as ecr_position_rank
    from board

),

joined as (

    select
        p.player_id,
        p.season,
        p.scoring_format,
        p.player_display_name,
        p.player_position,
        p.team,
        -- Exposed deliberately: this is the only key that reaches int_draft_board, and
        -- without it the documented "left-join from the board to see rookies" is
        -- impossible without routing back through staging. gsis ids do not reach ffverse.
        p.player_join_key,

        p.games_played,
        p.fantasy_points_total,
        p.fantasy_points_per_game,
        p.fantasy_points_stddev,
        p.fantasy_points_floor,
        p.fantasy_points_ceiling,

        p.targets,
        p.receptions,
        p.carries,
        p.receiving_air_yards,
        p.target_share_avg,
        p.air_yards_share_avg,

        p.production_position_rank,

        b.ecr,
        b.ecr_stddev,
        b.bye_week,
        b.ecr_position_rank,
        r.replacement_ppg,
        b.ecr is not null as is_on_draft_board,
        coalesce(b.ecr, 9999) <= {{ var('draftable_ecr_cutoff') }} as is_draftable

    from production_ranked as p
    left join board_ranked as b
        on
            p.player_join_key = b.player_join_key
            and p.player_position = b.player_position
            -- Consensus rank is scoring-specific; joining across formats would rank a
            -- standard league against PPR consensus.
            and p.scoring_format = b.scoring_format
    left join replacement as r
        on
            p.season = r.season
            and p.scoring_format = r.scoring_format
            and p.player_position = r.player_position

),

-- value_over_ecr compares two ranks, so both must be drawn from the same population.
-- production_position_rank spans everyone who played; ecr_position_rank spans only the
-- ~450 players on the board. Differencing them directly rewards fringe players for
-- being ranked at all -- a 6 ppg WR came out +83, ahead of every real pick. Re-ranking
-- production across board members only makes the two scales comparable.
comparable as (

    select
        *,
        case
            when is_on_draft_board and production_position_rank is not null
                then row_number() over (
                    partition by season, scoring_format, player_position
                    order by
                        case
                            when is_on_draft_board and production_position_rank is not null
                                then 0
                            else 1
                        end,
                        fantasy_points_per_game desc
                )
        end as board_production_rank
    from joined

),

valued as (

    select
        *,
        -- Positive = producing better than the market is charging.
        ecr_position_rank - board_production_rank as value_over_ecr,
        fantasy_points_per_game - replacement_ppg as points_over_replacement
    from comparable

),

-- The league-aware draft order. Unlike `overall` (consensus rank, identical in every
-- scoring format), this reorders when the rules change -- which is the entire point of
-- pricing a league's scoring rather than printing someone else's ranking.
draft_ordered as (

    select
        *,
        case
            when points_over_replacement is not null
                then row_number() over (
                    partition by season, scoring_format
                    order by
                        case when points_over_replacement is null then 1 else 0 end,
                        points_over_replacement desc
                )
        end as vor_draft_rank
    from valued

)

select
    player_id,
    season,
    scoring_format,
    player_display_name,
    player_position,
    team,
    player_join_key,
    cast(games_played as integer) as games_played,
    cast(fantasy_points_total as {{ dbt.type_numeric() }}) as fantasy_points_total,
    cast(fantasy_points_per_game as {{ dbt.type_numeric() }}) as fantasy_points_per_game,
    cast(fantasy_points_stddev as {{ dbt.type_numeric() }}) as fantasy_points_stddev,
    cast(fantasy_points_floor as {{ dbt.type_numeric() }}) as fantasy_points_floor,
    cast(fantasy_points_ceiling as {{ dbt.type_numeric() }}) as fantasy_points_ceiling,
    cast(targets as integer) as targets,
    cast(receptions as integer) as receptions,
    cast(carries as integer) as carries,
    cast(receiving_air_yards as {{ dbt.type_numeric() }}) as receiving_air_yards,
    cast(target_share_avg as {{ dbt.type_numeric() }}) as target_share_avg,
    cast(air_yards_share_avg as {{ dbt.type_numeric() }}) as air_yards_share_avg,
    cast(production_position_rank as integer) as production_position_rank,
    cast(board_production_rank as integer) as board_production_rank,
    cast(ecr as {{ dbt.type_numeric() }}) as ecr,
    cast(ecr_stddev as {{ dbt.type_numeric() }}) as ecr_stddev,
    cast(bye_week as integer) as bye_week,
    cast(ecr_position_rank as integer) as ecr_position_rank,
    cast(value_over_ecr as integer) as value_over_ecr,
    cast(replacement_ppg as {{ dbt.type_numeric() }}) as replacement_ppg,
    cast(points_over_replacement as {{ dbt.type_numeric() }}) as points_over_replacement,
    cast(vor_draft_rank as integer) as vor_draft_rank,
    is_on_draft_board,
    is_draftable
from draft_ordered
