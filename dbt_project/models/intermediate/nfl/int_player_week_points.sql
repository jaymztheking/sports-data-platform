-- Weekly fantasy points under every scoring format.
--
-- Scoring is applied here, at week grain, rather than in the mart, because the season
-- mart needs the *distribution* of weekly scores (stddev, floor, ceiling) and not just
-- the total. Aggregating first would throw that away.
--
-- Grain: player_id x season x week x scoring_format.

with weekly as (

    -- Offensive skill positions only. The scoring seed prices passing/rushing/receiving
    -- and nothing else, so an LB scores exactly 0.0 every week. Left in, those players
    -- rank as ties on zero and pollute every leaderboard downstream -- an LB shows up as
    -- "7th best at his position" on no production at all. Kickers and DST need their own
    -- scoring rules before they can be priced honestly.
    select * from {{ ref('stg_nfl__player_stats') }}
    where
        season_type = 'REG'
        and player_position in ('QB', 'RB', 'WR', 'TE')

),

-- The seed is long (one row per format per stat); widen it so scoring is a single
-- expression per row rather than a join per stat.
scoring as (

    select
        scoring_format,
        max(case when stat = 'passing_yards' then points_per_unit end) as w_passing_yards,
        max(case when stat = 'passing_tds' then points_per_unit end) as w_passing_tds,
        max(case when stat = 'interceptions' then points_per_unit end) as w_interceptions,
        max(case when stat = 'rushing_yards' then points_per_unit end) as w_rushing_yards,
        max(case when stat = 'rushing_tds' then points_per_unit end) as w_rushing_tds,
        max(case when stat = 'receptions' then points_per_unit end) as w_receptions,
        max(case when stat = 'receiving_yards' then points_per_unit end) as w_receiving_yards,
        max(case when stat = 'receiving_tds' then points_per_unit end) as w_receiving_tds,
        max(case when stat = 'fumbles_lost' then points_per_unit end) as w_fumbles_lost,
        max(case when stat = 'special_teams_tds' then points_per_unit end)
            as w_special_teams_tds,
        max(case when stat = 'two_point_conversions' then points_per_unit end)
            as w_two_point_conversions
    from {{ ref('scoring_rules') }}
    group by scoring_format

),

scored as (

    select
        w.player_id,
        w.season,
        w.week,
        w.player_display_name,
        w.player_position,
        w.player_join_key,
        w.team,
        s.scoring_format,

        w.targets,
        w.receptions,
        w.carries,
        w.receiving_air_yards,
        w.target_share,
        w.air_yards_share,

        coalesce(w.passing_yards, 0) * s.w_passing_yards
        + coalesce(w.passing_tds, 0) * s.w_passing_tds
        + coalesce(w.interceptions, 0) * s.w_interceptions
        + coalesce(w.rushing_yards, 0) * s.w_rushing_yards
        + coalesce(w.rushing_tds, 0) * s.w_rushing_tds
        + coalesce(w.receptions, 0) * s.w_receptions
        + coalesce(w.receiving_yards, 0) * s.w_receiving_yards
        + coalesce(w.receiving_tds, 0) * s.w_receiving_tds
        + coalesce(w.fumbles_lost, 0) * s.w_fumbles_lost
        -- Kick/punt return TDs. Omitting these was the entire gap against nflverse's
        -- own PPR column: 434 of 23,510 player-weeks, every one off by exactly -6.0,
        -- all return specialists. Reconciling against fantasy_points_ppr_source is what
        -- surfaced it -- worth keeping that column in staging for exactly this reason.
        + coalesce(w.special_teams_tds, 0) * s.w_special_teams_tds
        + coalesce(w.two_point_conversions, 0) * s.w_two_point_conversions as fantasy_points

    from weekly as w
    cross join scoring as s

)

select * from scored
