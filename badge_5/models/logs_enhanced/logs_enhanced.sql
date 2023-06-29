{{ config(
  materialized='table')}}

SELECT
    ip_address,
    GAMER_NAME,
    GAME_EVENT_NAME,
    GAME_EVENT_UTC,
    city,
    region,
    country,
    GAMER_LTZ_NAME,
    game_event_ltz,
    DOW_NAME,
    TOD_NAME
FROM (
    SELECT
        cdc.ip_address,
        cdc.user_login AS GAMER_NAME,
        cdc.user_event AS GAME_EVENT_NAME,
        cdc.datetime_iso8601 AS GAME_EVENT_UTC,
        loc.city,
        loc.region,
        loc.country,
        loc.timezone AS GAMER_LTZ_NAME,
        CONVERT_TIMEZONE('UTC', loc.timezone, cdc.datetime_iso8601) AS game_event_ltz,
        DAYNAME(game_event_ltz) AS DOW_NAME,
        tod.TOD_NAME
    FROM
        ed_cdc_stream cdc
        JOIN ipinfo_geoloc.demo.location loc ON ipinfo_geoloc.public.TO_JOIN_KEY(cdc.ip_address) = loc.join_key
        AND ipinfo_geoloc.public.TO_INT(cdc.ip_address) BETWEEN start_ip_int AND end_ip_int
        JOIN TIME_OF_DAY_LU tod ON HOUR(game_event_ltz) = tod.hour
)