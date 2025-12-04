{{
    config(
        materialized='incremental',
        unique_key='sale_id'
    )
}}

WITH int_sales AS (
    SELECT
        *
    FROM {{ ref('int_sales_prep') }}
),

final AS (
    SELECT
        sale_id,
        sales_person_id,
        car_id,
        sale_date,
        customer_name,
        sale_price,
        comm_rate,
        comm_earned,
        loaded_at

    FROM int_sales

{% if is_incremental()  %}

    WHERE loaded_at > (SELECT MAX(loaded_at) FROM {{ this }})

{% endif %}

)

SELECT
    *
FROM final


