{% macro generate_schema_name(custom_schema_name, node) -%}

    {%- set default_schema = target.schema -%}
    
    {# PROD #}
    {%- if target.name == 'prod' and custom_schema_name is not none -%}

        {{ default_schema }}_{{ custom_schema_name | trim }}

    {# DEV #}
    {%- else -%}

        {{ default_schema }}

    {%- endif -%}

{%- endmacro %}