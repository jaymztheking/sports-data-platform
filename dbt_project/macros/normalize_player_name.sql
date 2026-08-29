{#
    One definition of the player-name join key, used by stg_nfl__player_stats and
    stg_nfl__ff_rankings. The two feeds share no player id — gsis on the stats side,
    ffverse on the board side — so a normalised name is the only bridge.

    Two feeds, two naming styles:
      - nflverse writes "Patrick Mahomes",     the board writes "Patrick Mahomes II"
      - nflverse writes "Travis Etienne",      the board writes "Travis Etienne Jr."
    Left unstripped, generational suffixes silently drop four of the top-60 2025 PPR
    scorers (Mahomes, James Cook, Etienne, Pitts) out of the draft board — a failure
    that looks like "those players just aren't ranked" rather than like a bug.

    Steps: lowercase -> strip . ' - -> drop a trailing generational suffix -> trim.
    `regexp_replace` is available on both DuckDB and Postgres, so this stays portable.
#}
{% macro normalize_player_name(column) -%}
    trim(
        regexp_replace(
            replace(replace(replace(lower(trim({{ column }})), '.', ''), '''', ''), '-', ''),
            '\s+(jr|sr|iv|iii|ii|v)$',
            ''
        )
    )
{%- endmacro %}
