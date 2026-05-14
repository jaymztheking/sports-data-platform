with source as (
    select * from {{ source('raw_mlb', 'batting') }}
),

renamed as (
    select
        "IDfg"::int as player_id_fg,
        "Name" as player_name,
        "Team" as team,
        "Season"::int as season,
        "G"::int as games,
        "AB"::int as at_bats,
        "PA"::int as plate_appearances,
        "H"::int as hits,
        "1B"::int as singles,
        "2B"::int as doubles,
        "3B"::int as triples,
        "HR"::int as home_runs,
        "R"::int as runs,
        "RBI"::int as rbi,
        "BB"::int as walks,
        "SO"::int as strikeouts,
        "AVG"::numeric(4, 3) as batting_avg,
        "OBP"::numeric(4, 3) as on_base_pct,
        "SLG"::numeric(4, 3) as slugging_pct,
        "OPS"::numeric(4, 3) as ops,
        "wOBA"::numeric(4, 3) as woba,
        "WAR"::numeric(4, 1) as war,
        ingested_at::timestamp as ingested_at
    from source
)

select * from renamed
