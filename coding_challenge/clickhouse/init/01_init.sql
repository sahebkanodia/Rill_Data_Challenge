-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS taxi_db;

-- Set up permissions
-- GRANT ALL ON taxi_db.* TO default;

-- Create table if it doesn't exist
CREATE TABLE IF NOT EXISTS taxi_db.taxi_trips (
    tpep_pickup_datetime DateTime,
    tpep_dropoff_datetime DateTime,
    pickup_datetime Date,
    PULocationID Int32,
    DOLocationID Int32,
    trip_distance Float64,
    fare_amount Float64,
    tip_amount Float64,
    total_amount Float64,
    payment_type String,
    trip_duration Float64,
    hour_of_day String,
    pickup_borough String,
    pickup_zone String,
    dropoff_borough String,
    dropoff_zone String,
    _version UInt64
)
ENGINE = ReplacingMergeTree(_version)
PARTITION BY pickup_datetime
ORDER BY (
    tpep_pickup_datetime,
    tpep_dropoff_datetime,
    pickup_datetime,
    PULocationID,
    DOLocationID,
    trip_distance,
    fare_amount,
    tip_amount,
    total_amount,
    payment_type,
    trip_duration,
    hour_of_day,
    pickup_borough,
    pickup_zone,
    dropoff_borough,
    dropoff_zone
)
SETTINGS index_granularity = 8192; 