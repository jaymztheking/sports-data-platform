{#
    Schema resolution keyed on target.name — the one place env separation lives.

    dev (DuckDB):   everything lands in the flat `dev` schema, so builds are
                    disposable (CI runs this same target ephemerally on :memory:).
    prod (Postgres): custom schema names are honored, so layers land in real schemas
                    (e.g. a marts model configured with +schema: marts -> `marts`).
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if target.name == 'prod' and custom_schema_name is not none -%}
        {{ custom_schema_name | trim }}
    {%- else -%}
        {{ target.schema }}
    {%- endif -%}
{%- endmacro %}
