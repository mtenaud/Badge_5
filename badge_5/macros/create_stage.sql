{% macro create_stage(stage_name, stage_url, schema_name = target.schema, db_name = target.database, dry_run = True) %}

    {% set sql %}
        create or replace stage {{ db_name }}.{{ schema_name }}.{{ stage_name }}
        url={{stage_url}};
    {% endset %}

    {% if not dry_run %}
        {% do run_query(sql) %}
    {% else %}
        {{ log(sql, info=True) }}
    {% endif %}

{% endmacro %}