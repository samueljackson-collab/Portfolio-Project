-- Flink SQL Queries for Real-time Data Streaming
-- These queries define tables, views, and continuous queries for stream processing

-- ============================================================================
-- Source Tables (Kafka Topics)
-- ============================================================================

-- User events table (from Kafka)
CREATE TABLE user_events (
    event_id STRING,
    user_id STRING,
    session_id STRING,
    event_type STRING,
    event_time TIMESTAMP(3),
    page_url STRING,
    user_agent STRING,
    ip_address STRING,
    device_type STRING,
    properties MAP<STRING, STRING>,
    WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
) WITH (
    'connector' = 'kafka',
    'topic' = 'user-events',
    'properties.bootstrap.servers' = 'localhost:9092',
    'properties.group.id' = 'flink-sql-consumer',
    'scan.startup.mode' = 'latest-offset',
    'format' = 'json',
    'json.timestamp-format.standard' = 'ISO-8601'
);

-- User events with Avro schema
CREATE TABLE user_events_avro (
    event_id STRING,
    user_id STRING,
    session_id STRING,
    event_type STRING,
    event_time TIMESTAMP(3),
    page_url STRING,
    referrer STRING,
    user_agent STRING,
    ip_address STRING,
    device_type STRING,
    properties MAP<STRING, STRING>,
    metadata ROW<producer_id STRING, schema_version STRING, environment STRING>,
    WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
) WITH (
    'connector' = 'kafka',
    'topic' = 'user-events-avro',
    'properties.bootstrap.servers' = 'localhost:9092',
    'properties.group.id' = 'flink-sql-avro-consumer',
    'scan.startup.mode' = 'latest-offset',
    'format' = 'avro-confluent',
    'avro-confluent.url' = 'http://localhost:8081'
);

-- ============================================================================
-- Sink Tables (Output Destinations)
-- ============================================================================

-- Event counts sink (to Kafka)
CREATE TABLE event_counts_sink (
    event_type STRING,
    count_value BIGINT,
    window_start TIMESTAMP(3),
    window_end TIMESTAMP(3),
    PRIMARY KEY (event_type, window_start) NOT ENFORCED
) WITH (
    'connector' = 'kafka',
    'topic' = 'event-counts',
    'properties.bootstrap.servers' = 'localhost:9092',
    'format' = 'json'
);

-- User activity sink
CREATE TABLE user_activity_sink (
    user_id STRING,
    event_count BIGINT,
    unique_sessions BIGINT,
    window_start TIMESTAMP(3),
    window_end TIMESTAMP(3),
    PRIMARY KEY (user_id, window_start) NOT ENFORCED
) WITH (
    'connector' = 'kafka',
    'topic' = 'user-activity',
    'properties.bootstrap.servers' = 'localhost:9092',
    'format' = 'json'
);

-- Revenue metrics sink
CREATE TABLE revenue_sink (
    total_revenue DOUBLE,
    order_count BIGINT,
    avg_order_value DOUBLE,
    window_start TIMESTAMP(3),
    window_end TIMESTAMP(3)
) WITH (
    'connector' = 'kafka',
    'topic' = 'revenue-metrics',
    'properties.bootstrap.servers' = 'localhost:9092',
    'format' = 'json'
);

-- ============================================================================
-- Views and Continuous Queries
-- ============================================================================

-- View: Real-time event counts by type (1-minute tumbling window)
CREATE VIEW event_counts AS
SELECT
    event_type,
    COUNT(*) as count_value,
    TUMBLE_START(event_time, INTERVAL '1' MINUTE) as window_start,
    TUMBLE_END(event_time, INTERVAL '1' MINUTE) as window_end
FROM user_events
GROUP BY
    event_type,
    TUMBLE(event_time, INTERVAL '1' MINUTE);

-- View: User activity by minute
CREATE VIEW user_activity_by_minute AS
SELECT
    user_id,
    COUNT(*) as event_count,
    COUNT(DISTINCT session_id) as unique_sessions,
    TUMBLE_START(event_time, INTERVAL '1' MINUTE) as window_start,
    TUMBLE_END(event_time, INTERVAL '1' MINUTE) as window_end
FROM user_events
GROUP BY
    user_id,
    TUMBLE(event_time, INTERVAL '1' MINUTE);

-- View: Revenue metrics (5-minute tumbling window)
CREATE VIEW revenue_metrics AS
SELECT
    SUM(CAST(properties['amount'] AS DOUBLE)) as total_revenue,
    COUNT(*) as order_count,
    AVG(CAST(properties['amount'] AS DOUBLE)) as avg_order_value,
    TUMBLE_START(event_time, INTERVAL '5' MINUTE) as window_start,
    TUMBLE_END(event_time, INTERVAL '5' MINUTE) as window_end
FROM user_events
WHERE event_type = 'PURCHASE'
  AND properties['amount'] IS NOT NULL
GROUP BY TUMBLE(event_time, INTERVAL '5' MINUTE);

-- View: Session analysis (30-minute sliding window)
CREATE VIEW session_analysis AS
SELECT
    session_id,
    COUNT(*) as event_count,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(DISTINCT event_type) as event_type_count,
    MIN(event_time) as session_start,
    MAX(event_time) as session_end,
    HOP_START(event_time, INTERVAL '5' MINUTE, INTERVAL '30' MINUTE) as window_start,
    HOP_END(event_time, INTERVAL '5' MINUTE, INTERVAL '30' MINUTE) as window_end
FROM user_events
WHERE session_id IS NOT NULL
GROUP BY
    session_id,
    HOP(event_time, INTERVAL '5' MINUTE, INTERVAL '30' MINUTE);

-- View: Top pages by views (1-minute tumbling window)
CREATE VIEW top_pages AS
SELECT
    page_url,
    COUNT(*) as view_count,
    TUMBLE_START(event_time, INTERVAL '1' MINUTE) as window_start,
    TUMBLE_END(event_time, INTERVAL '1' MINUTE) as window_end
FROM user_events
WHERE event_type = 'PAGE_VIEW'
  AND page_url IS NOT NULL
GROUP BY
    page_url,
    TUMBLE(event_time, INTERVAL '1' MINUTE);

-- View: Device distribution
CREATE VIEW device_distribution AS
SELECT
    device_type,
    COUNT(*) as count_value,
    TUMBLE_START(event_time, INTERVAL '5' MINUTE) as window_start,
    TUMBLE_END(event_time, INTERVAL '5' MINUTE) as window_end
FROM user_events
WHERE device_type IS NOT NULL
GROUP BY
    device_type,
    TUMBLE(event_time, INTERVAL '5' MINUTE);

-- View: Conversion funnel (5-minute window)
CREATE VIEW conversion_funnel AS
SELECT
    TUMBLE_START(event_time, INTERVAL '5' MINUTE) as window_start,
    TUMBLE_END(event_time, INTERVAL '5' MINUTE) as window_end,
    COUNT(CASE WHEN event_type = 'PAGE_VIEW' THEN 1 END) as page_views,
    COUNT(CASE WHEN event_type = 'ADD_TO_CART' THEN 1 END) as add_to_cart,
    COUNT(CASE WHEN event_type = 'PURCHASE' THEN 1 END) as purchases,
    COUNT(DISTINCT user_id) as unique_users
FROM user_events
GROUP BY TUMBLE(event_time, INTERVAL '5' MINUTE);

-- View: Search analytics
CREATE VIEW search_analytics AS
SELECT
    properties['query'] as search_query,
    COUNT(*) as search_count,
    AVG(CAST(properties['results_count'] AS INTEGER)) as avg_results,
    TUMBLE_START(event_time, INTERVAL '10' MINUTE) as window_start,
    TUMBLE_END(event_time, INTERVAL '10' MINUTE) as window_end
FROM user_events
WHERE event_type = 'SEARCH'
  AND properties['query'] IS NOT NULL
GROUP BY
    properties['query'],
    TUMBLE(event_time, INTERVAL '10' MINUTE);

-- View: User engagement score (15-minute sliding window)
CREATE VIEW user_engagement AS
SELECT
    user_id,
    COUNT(*) as total_events,
    COUNT(DISTINCT event_type) as event_diversity,
    COUNT(DISTINCT session_id) as session_count,
    SUM(CASE WHEN event_type = 'PURCHASE' THEN 1 ELSE 0 END) as purchases,
    (COUNT(*) * 0.3 +
     COUNT(DISTINCT event_type) * 0.3 +
     SUM(CASE WHEN event_type = 'PURCHASE' THEN 1 ELSE 0 END) * 0.4) as engagement_score,
    HOP_START(event_time, INTERVAL '5' MINUTE, INTERVAL '15' MINUTE) as window_start,
    HOP_END(event_time, INTERVAL '5' MINUTE, INTERVAL '15' MINUTE) as window_end
FROM user_events
GROUP BY
    user_id,
    HOP(event_time, INTERVAL '5' MINUTE, INTERVAL '15' MINUTE);

-- ============================================================================
-- Insert Statements (Continuous Queries)
-- ============================================================================

-- Continuously write event counts to sink
INSERT INTO event_counts_sink
SELECT event_type, count_value, window_start, window_end
FROM event_counts;

-- Continuously write user activity to sink
INSERT INTO user_activity_sink
SELECT user_id, event_count, unique_sessions, window_start, window_end
FROM user_activity_by_minute;

-- Continuously write revenue metrics to sink
INSERT INTO revenue_sink
SELECT total_revenue, order_count, avg_order_value, window_start, window_end
FROM revenue_metrics;

-- ============================================================================
-- Utility Queries
-- ============================================================================

-- Get current event rate (last 1 minute)
SELECT
    COUNT(*) / 60.0 as events_per_second,
    TUMBLE_START(event_time, INTERVAL '1' MINUTE) as window_start
FROM user_events
GROUP BY TUMBLE(event_time, INTERVAL '1' MINUTE);

-- Get most active users (last 5 minutes)
SELECT
    user_id,
    COUNT(*) as event_count
FROM user_events
WHERE event_time > CURRENT_TIMESTAMP - INTERVAL '5' MINUTE
GROUP BY user_id
ORDER BY event_count DESC
LIMIT 10;

-- Get event type distribution (realtime)
SELECT
    event_type,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentage
FROM user_events
GROUP BY event_type;
