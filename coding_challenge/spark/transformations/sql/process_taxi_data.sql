WITH base_calculations AS (
  SELECT 
    tpep_pickup_datetime,
    tpep_dropoff_datetime,
    to_date(tpep_pickup_datetime) as pickup_datetime,
    PULocationID,
    DOLocationID,
    trip_distance,
    fare_amount,
    tip_amount,
    total_amount,
    payment_type,
    -- trip duration calculation
    ROUND((unix_timestamp(tpep_dropoff_datetime) - unix_timestamp(tpep_pickup_datetime)) / 60.0, 2) as trip_duration,
    -- Hour of day calculation
    date_format(tpep_pickup_datetime, 'HH') as hour_of_day,
    -- Version with IST timestamp for Sort key
    unix_timestamp(from_utc_timestamp(current_timestamp(), 'Asia/Kolkata')) as _version
  FROM {{ taxi_table }}
),
-- Join with zone data
zone_enriched AS (
  SELECT 
    b.tpep_pickup_datetime,
    b.tpep_dropoff_datetime,
    b.pickup_datetime,
    b.PULocationID,
    b.DOLocationID,
    b.trip_distance,
    b.fare_amount,
    b.tip_amount,
    b.total_amount,
    b.payment_type,
    b.trip_duration,
    b.hour_of_day,
    pz.Borough as pickup_borough,
    pz.Zone as pickup_zone,
    dz.Borough as dropoff_borough,
    dz.Zone as dropoff_zone,
    b._version
  FROM base_calculations b
  LEFT JOIN {{ zone_table }} pz ON b.PULocationID = pz.LocationID
  LEFT JOIN {{ zone_table }} dz ON b.DOLocationID = dz.LocationID
)
-- Final select
SELECT * FROM zone_enriched 