-- Draft-day query. Compile with:
--   dbt compile -s draft_board --project-dir dbt_project --profiles-dir dbt_project
-- then run the SQL, or just query fct_player_season directly.
--
-- Ranks the draftable pool by how much better a player produced last season than the
-- market is charging for him. `is_draftable` is doing real work here: without it the
-- tail of the board floods the top of this list.
select
    player_display_name,
    player_position,
    team,
    ecr,
    ecr_position_rank,
    board_production_rank,
    value_over_ecr,
    games_played,
    fantasy_points_per_game,
    fantasy_points_floor,
    fantasy_points_ceiling,
    fantasy_points_stddev,
    target_share_avg,
    bye_week
from {{ ref('fct_player_season') }}
where season = {{ var('default_season', 2025) }}
    and scoring_format = 'ppr'
    and is_draftable
order by value_over_ecr desc
