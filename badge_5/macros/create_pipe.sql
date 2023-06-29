{% macro create_pipe(pipe_name, table_name, schema_name = target.schema, db_name = target.database, dry_run = True) %}

    {% set sql %}
        CREATE or replace PIPE {{ db_name }}.{{ schema_name }}.{{pipe_name}}
        auto_ingest=true
        aws_sns_topic='arn:aws:sns:us-west-2:321463406630:dngw_topic'
        AS 
        COPY INTO {{table_name}}
        FROM (
            SELECT 
                METADATA$FILENAME as log_file_name, 
                METADATA$FILE_ROW_NUMBER as log_file_row_id,
                current_timestamp(0) as load_ltz,
                get($1,'datetime_iso8601')::timestamp_ntz as DATETIME_ISO8601,
                get($1,'user_event')::text as USER_EVENT,
                get($1,'user_login')::text as USER_LOGIN,
                get($1,'ip_address')::text as IP_ADDRESS
            FROM @uni_kishore_pipeline
        )
        file_format = (format_name = ff_json_logs);
    {% endset %}

    {% if not dry_run %}
        {% do run_query(sql) %}
    {% else %}
        {{ log(sql, info=True) }}
    {% endif %}

{% endmacro %}