WITH int_sales AS (
    SELECT
        *
    FROM {{ ref('int_sales_prep') }}
),

distinct_cars AS (
    SELECT
        DISTINCT
        car_id,
        car_make,
        car_model,
        car_year

    FROM int_sales
)

SELECT
    *
FROM distinct_cars