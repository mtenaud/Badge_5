{% macro get_stream_value(stream_name, schema_name = target.schema, db_name = target.database, dry_run = True) %}

    {% set sql %}
        create or replace view result as
        select system$stream_has_data('{{stream_name}}') as bool;
    {% endset %}

    {% if not dry_run %}
        {% do run_query(sql) %}
    {% else %}
        {{ log(sql, info=True) }}
    {% endif %}

{% endmacro %}