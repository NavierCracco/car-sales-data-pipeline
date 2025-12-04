WITH source AS (
    SELECT
        *
    FROM {{ source('raw_bi_car', 'CAR_SALES') }}
),

renamed AS (
    SELECT
        TRY_TO_DATE("Date", 'YYYY-MM-DD') AS sale_date,

        TRIM("Salesperson") AS sales_person,
        TRIM("Customer Name") AS customer_name,
        TRIM("Car Make") AS car_make,
        TRIM("Car Model") AS car_model,

        TRY_CAST("Car Year" AS INTEGER) AS car_year,
        TRY_CAST("Sale Price" AS NUMERIC(12, 2)) AS sale_price,
        TRY_CAST("Commission Rate" AS NUMERIC(10, 5)) AS comm_rate,
        TRY_CAST("Commission Earned" AS NUMERIC(10, 2)) AS comm_earned,

        TO_TIMESTAMP_NTZ("_LOADED_AT", 6) AS loaded_at,

        _SOURCE_FILE AS source_file
    FROM source
)

SELECT 
    *
FROM renamed
WHERE sale_date IS NOT NULL