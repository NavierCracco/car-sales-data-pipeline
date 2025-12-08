WITH stg_sales AS (
    SELECT
        *
    FROM {{ ref('stg_car_sales') }}
),

with_keys AS (
    SELECT
        *,

        -- Generate a unique ID for the sale (Fact Key)
        {{ dbt_utils.generate_surrogate_key([
            'sale_date',
            'customer_name',
            'sale_price',
            'sales_person'
        ]) }} AS sale_id,

        -- Generate ID for sales person (Dim Key)
        {{ dbt_utils.generate_surrogate_key([
            'sales_person'
        ])}} AS sales_person_id,

        -- Generate ID for Car (Dim Key)
        {{ dbt_utils.generate_surrogate_key([
            'car_make',
            'car_model',
            'car_year'
        ]) }} AS car_id

    FROM stg_sales
)

SELECT
    *
FROM with_keys