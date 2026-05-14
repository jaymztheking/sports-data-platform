with source as (
    select * from {{ source('raw_mlb', 'schedules') }}
),

renamed as (
    select
        "Date"::date as game_date,
        "Tm" as team,
        "Opp" as opponent,
        "W/L" as result,
        "R"::int as runs_scored,
        "RA"::int as runs_allowed,
        "Win" as winning_pitcher,
        "Loss" as losing_pitcher,
        "Save" as save_pitcher,
        season::int as season,
        ingested_at::timestamp as ingested_at
    from source
)

select * from renamed
