with source as (
    select * from {{ source('raw_mlb', 'pitching') }}
),

renamed as (
    select
        "IDfg"::int as player_id_fg,
        "Name" as player_name,
        "Team" as team,
        "Season"::int as season,
        "W"::int as wins,
        "L"::int as losses,
        "ERA"::numeric(5, 2) as era,
        "G"::int as games,
        "GS"::int as games_started,
        "IP"::numeric(5, 1) as innings_pitched,
        "SO"::int as strikeouts,
        "BB"::int as walks,
        "H"::int as hits_allowed,
        "HR"::int as home_runs_allowed,
        "WHIP"::numeric(4, 2) as whip,
        "K/9"::numeric(4, 1) as k_per_9,
        "BB/9"::numeric(4, 1) as bb_per_9,
        "FIP"::numeric(5, 2) as fip,
        "WAR"::numeric(4, 1) as war,
        ingested_at::timestamp as ingested_at
    from source
)

select * from renamed
