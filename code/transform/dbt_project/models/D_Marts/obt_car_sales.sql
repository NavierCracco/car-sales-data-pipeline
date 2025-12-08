{{
    config(
        materialized='table',
    )
}}

WITH fct_sales AS (
    SELECT
        *
    FROM {{ ref('fct_car_sales') }}
),

dim_cars AS (
    SELECT
        *
    FROM {{ ref('dim_cars') }}
),

dim_salespeople AS (
    SELECT
        *
    FROM {{ ref('dim_salespeople') }}
),

final AS (
    SELECT
        f.sale_id,
        f.sale_date,
        f.customer_name,
        f.comm_rate,
        f.comm_earned,
        f.sale_price,

        c.car_make,
        c.car_model,
        c.car_year,

        s.sales_person AS sales_person_name,

        f.loaded_at


    FROM fct_sales f

    LEFT JOIN dim_cars c
        ON f.car_id = c.car_id

    LEFT JOIN dim_salespeople s
        ON f.sales_person_id = s.sales_person_id
    
)

SELECT
    *
FROM final