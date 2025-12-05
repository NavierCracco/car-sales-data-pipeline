{{
    config(
        materialized='table'
    )
}}

WITH int_sales AS (
    SELECT
        *
    FROM {{ ref('int_sales_prep') }}
),

distinct_salespeople AS (
    SELECT
        DISTINCT
        sales_person_id,
        sales_person

    FROM int_sales
)

SELECT
    *
FROM distinct_salespeople