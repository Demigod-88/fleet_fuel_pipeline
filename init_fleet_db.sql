-- init_fleet_db.sql

-- 1. Dimension Tables
CREATE TABLE IF NOT EXISTS dim_vehicle (
    vehicle_id VARCHAR(50) PRIMARY KEY,
    license_plate VARCHAR(20) NOT NULL,
    make_model VARCHAR(50) NOT NULL,
    max_tank_capacity_l NUMERIC(6,2) NOT NULL,
    primary_depot VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_fuel_card (
    card_number VARCHAR(50) PRIMARY KEY,
    vehicle_id VARCHAR(50) REFERENCES dim_vehicle(vehicle_id),
    driver_name VARCHAR(100) NOT NULL,
    card_status VARCHAR(20) DEFAULT 'ACTIVE'
);

-- 2. Raw Staging Tables
CREATE TABLE IF NOT EXISTS raw_fuel_transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    card_number VARCHAR(50) NOT NULL,
    transaction_time TIMESTAMP NOT NULL,
    station_id VARCHAR(50) NOT NULL,
    station_lat NUMERIC(9,6) NOT NULL,
    station_long NUMERIC(9,6) NOT NULL,
    volume_liters NUMERIC(6,2) NOT NULL,
    total_cost NUMERIC(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS raw_telematics_logs (
    telematics_event_id SERIAL PRIMARY KEY,
    vehicle_id VARCHAR(50) NOT NULL,
    ping_time TIMESTAMP NOT NULL,
    gps_lat NUMERIC(9,6) NOT NULL,
    gps_long NUMERIC(9,6) NOT NULL,
    fuel_level_pct NUMERIC(5,2) NOT NULL,
    odometer_km NUMERIC(10,2) NOT NULL
);

-- 3. Analytical Fact Table
CREATE TABLE IF NOT EXISTS fact_fuel_reconciliation (
    transaction_id VARCHAR(50) PRIMARY KEY,
    vehicle_id VARCHAR(50) NOT NULL,
    card_number VARCHAR(50) NOT NULL,
    transaction_time TIMESTAMP NOT NULL,
    volume_purchased_l NUMERIC(6,2) NOT NULL,
    fuel_added_telemetry_l NUMERIC(6,2),
    distance_station_to_vehicle_km NUMERIC(6,2),
    flag_location_mismatch BOOLEAN DEFAULT FALSE,
    flag_volume_overflow BOOLEAN DEFAULT FALSE,
    flag_fuel_discrepancy BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);