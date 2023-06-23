{% macro create_file_format(file_format_name, file_format_type, strip_outer_array, schema_name = target.schema, db_name = target.database, dry_run = True) %}

    {% set sql %}
        create or replace file format {{ db_name }}.{{ schema_name }}.{{ file_format_name }}
        type={{file_format_type}},
        strip_outer_array={{strip_outer_array}};
    {% endset %}

    {% if not dry_run %}
        {% do run_query(sql) %}
    {% else %}
        {{ log(sql, info=True) }}
    {% endif %}

{% endmacro %}