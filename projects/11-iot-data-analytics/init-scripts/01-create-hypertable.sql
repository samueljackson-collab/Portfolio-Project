-- Create TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- This script is automatically executed by TimescaleDB container
-- The actual table creation is handled by mqtt_processor.py to ensure
-- it's created with the correct schema and indexes
