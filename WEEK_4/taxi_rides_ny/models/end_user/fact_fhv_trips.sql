{{ config(materialized="table") }}

WITH fhv_trips AS (
    SELECT *, 
        "FHV" AS service_type 
    FROM {{ ref("stg_fhv_tripdata") }}
),
dim_zones AS (
    SELECT * FROM {{ ref("dim_zones") }}
    WHERE borough != "Unknown"
)
SELECT
    fhv_trips.tripid,
    fhv_trips.dispatching_base_num,
    fhv_trips.service_type,
    fhv_trips.pickup_locationid,
    pickup_zone.borough as pickup_borough,
    pickup_zone.zone as pickup_zone,
    fhv_trips.dropoff_locationid,
    dropoff_zone.borough as dropoff_borough,
    dropoff_zone.zone as dropoff_zone,
    fhv_trips.pickup_datetime,
    fhv_trips.dropoff_datetime,
    fhv_trips.sr_flag
FROM fhv_trips
INNER JOIN dim_zones AS pickup_zone
ON fhv_trips.pickup_locationid = pickup_zone.locationid
INNER JOIN dim_zones AS dropoff_zone
ON fhv_trips.dropoff_locationid = dropoff_zone.locationid