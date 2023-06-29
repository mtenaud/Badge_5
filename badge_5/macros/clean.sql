{% macro clean(schema_name = target.schema, db_name = target.database, dry_run = True) %}

    {% set sql %}
        drop table time_of_day_lu;
        drop file format ff_json_logs;
        drop stage uni_kishore_pipeline;
        drop table ed_pipeline_logs;
        drop pipe get_new_files;
        drop stream ed_cdc_stream;
        drop table logs_enhanced;
    {% endset %}

    {% if not dry_run %}
        {% do run_query(sql) %}
    {% else %}
        {{ log(sql, info=True) }}
    {% endif %}

{% endmacro %}