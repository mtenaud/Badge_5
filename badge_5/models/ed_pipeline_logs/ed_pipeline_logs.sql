{{ config(
  materialized='table')}}

  SELECT 
    METADATA$FILENAME as log_file_name, 
    METADATA$FILE_ROW_NUMBER as log_file_row_id,
    current_timestamp(0) as load_ltz,
    get($1,'datetime_iso8601')::timestamp_ntz as DATETIME_ISO8601,
    get($1,'user_event')::text as USER_EVENT,
    get($1,'user_login')::text as USER_LOGIN,
    get($1,'ip_address')::text as IP_ADDRESS
  FROM @uni_kishore_pipeline
  (file_format => 'ff_json_logs')