{% macro create_stream(stream_name, table_name, schema_name = target.schema, db_name = target.database, dry_run = True) %}

    {% set sql %}
        create or replace stream {{ db_name }}.{{ schema_name }}.{{stream_name}}
            on table {{ db_name }}.{{ schema_name }}.{{table_name}};
    {% endset %}

    {% if not dry_run %}
        {% do run_query(sql) %}
    {% else %}
        {{ log(sql, info=True) }}
    {% endif %}

{% endmacro %}