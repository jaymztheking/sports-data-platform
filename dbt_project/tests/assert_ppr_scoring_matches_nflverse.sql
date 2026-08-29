-- Our seed-driven PPR must reproduce nflverse's own fantasy_points_ppr exactly.
--
-- This is the test that earned its keep. It caught two silent gaps in the seed:
-- return touchdowns (434 player-weeks off by exactly -6.0) and two-point conversions
-- (385 off by multiples of -2.0). Both presented as slightly-low players, not as bugs.
--
-- Any row returned is a disagreement, so this fails loudly if the seed drifts.
select
    w.player_id,
    w.season,
    w.week,
    w.fantasy_points as our_points,
    s.fantasy_points_ppr_source as nflverse_points
from {{ ref('int_player_week_points') }} as w
inner join {{ ref('stg_nfl__player_stats') }} as s
    on
        w.player_id = s.player_id
        and w.season = s.season
        and w.week = s.week
        and s.season_type = 'REG'
where
    w.scoring_format = 'ppr'
    and abs(w.fantasy_points - s.fantasy_points_ppr_source) > 0.01
