{#
    Schema resolution keyed on target.name — the one place env separation lives.

    dev / ci (DuckDB):  everything lands in the target's own flat schema (`dev` / `ci`),
                        so builds are disposable and the two envs never collide.
    prod  (Postgres):   custom schema names are honored, so layers land in real schemas
                        (e.g. a marts model configured with +schema: marts -> `marts`).
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if target.name == 'prod' and custom_schema_name is not none -%}
        {{ custom_schema_name | trim }}
    {%- else -%}
        {{ target.schema }}
    {%- endif -%}
{%- endmacro %}
