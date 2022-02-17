{{ config(materialized="view") }}

SELECT
    -- identifiers
    {{ dbt_utils.surrogate_key(["dispatching_base_num", "pickup_datetime"]) }} AS tripid,
    cast(dispatching_base_num as string) as dispatching_base_num,
    cast(pulocationid as integer) as pickup_locationid,
    cast(dolocationid as integer) as dropoff_locationid,
    
    -- timestamps
    cast(pickup_datetime as timestamp) as pickup_datetime,
    cast(dropoff_datetime as timestamp) as dropoff_datetime,
    
    -- trip info
    cast(sr_flag as integer) as sr_flag

FROM {{ source("staging", "external_table_fhv") }}
-- dbt run --var "is_test_run: false"
{% if var("is_test_run", default=true) %}

LIMIT 100

{% endif %}