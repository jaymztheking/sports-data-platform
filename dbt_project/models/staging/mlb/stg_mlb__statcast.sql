with source as (
    select * from {{ source('raw_mlb', 'statcast') }}
),

renamed as (
    select
        game_pk::bigint as game_id,
        game_date::date as game_date,
        batter::int as batter_id,
        pitcher::int as pitcher_id,
        events as event_type,
        description as pitch_description,
        pitch_type,
        release_speed::numeric(5, 1) as release_speed_mph,
        release_spin_rate::numeric(7, 1) as release_spin_rate,
        launch_speed::numeric(5, 1) as launch_speed_mph,
        launch_angle::numeric(5, 1) as launch_angle,
        hit_distance_sc::numeric(6, 1) as hit_distance,
        estimated_ba_using_speedangle::numeric(4, 3) as xba,
        estimated_woba_using_speedangle::numeric(4, 3) as xwoba,
        home_team,
        away_team,
        inning::int as inning,
        inning_topbot as half_inning,
        at_bat_number::int as at_bat_number,
        pitch_number::int as pitch_number,
        stand as batter_side,
        p_throws as pitcher_hand,
        zone::int as zone,
        ingested_at::timestamp as ingested_at
    from source
)

select * from renamed
