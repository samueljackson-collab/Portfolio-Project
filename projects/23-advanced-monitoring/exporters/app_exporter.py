#!/usr/bin/env python3
"""Custom Application Metrics Exporter for Prometheus.

This exporter collects application-specific metrics and exposes them
in Prometheus format. It demonstrates custom metric collection, caching,
and production-ready patterns for monitoring business metrics.
"""
import time
import logging
import random
import argparse
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
import os

from prometheus_client import (
    start_http_server,
    Gauge,
    Counter,
    Histogram,
    Summary,
    Info,
    Enum,
    generate_latest,
    REGISTRY
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# Application Metrics
# =============================================================================

# Business Metrics
app_requests_total = Counter(
    'app_requests_total',
    'Total number of application requests',
    ['method', 'endpoint', 'status']
)

app_active_users = Gauge(
    'app_active_users',
    'Number of currently active users',
    ['user_type']
)

app_revenue_total = Counter(
    'app_revenue_total_usd',
    'Total revenue in USD',
    ['product', 'region']
)

app_transactions_total = Counter(
    'app_transactions_total',
    'Total number of transactions',
    ['type', 'status']
)

# Performance Metrics
app_request_duration_seconds = Histogram(
    'app_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint'],
    buckets=[.005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 2.5, 5.0, 7.5, 10.0]
)

app_request_size_bytes = Summary(
    'app_request_size_bytes',
    'Request size in bytes',
    ['method', 'endpoint']
)

app_response_size_bytes = Summary(
    'app_response_size_bytes',
    'Response size in bytes',
    ['method', 'endpoint']
)

# Database Metrics
app_db_connections_active = Gauge(
    'app_db_connections_active',
    'Active database connections',
    ['pool', 'database']
)

app_db_query_duration_seconds = Histogram(
    'app_db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type', 'table'],
    buckets=[.001, .005, .01, .025, .05, .1, .25, .5, 1.0]
)

app_db_errors_total = Counter(
    'app_db_errors_total',
    'Total database errors',
    ['database', 'error_type']
)

# Cache Metrics
app_cache_hits_total = Counter(
    'app_cache_hits_total',
    'Total cache hits',
    ['cache']
)

app_cache_misses_total = Counter(
    'app_cache_misses_total',
    'Total cache misses',
    ['cache']
)

app_cache_size_bytes = Gauge(
    'app_cache_size_bytes',
    'Cache size in bytes',
    ['cache']
)

# Queue Metrics
app_queue_depth = Gauge(
    'app_queue_depth',
    'Number of items in queue',
    ['queue']
)

app_queue_processing_duration_seconds = Histogram(
    'app_queue_processing_duration_seconds',
    'Queue item processing duration',
    ['queue'],
    buckets=[.1, .5, 1, 2.5, 5, 10, 30, 60]
)

# Error Metrics
app_errors_total = Counter(
    'app_errors_total',
    'Total application errors',
    ['error_type', 'severity']
)

app_error_rate = Gauge(
    'app_error_rate',
    'Application error rate (errors per second)',
    ['window']
)

# SLO Metrics
app_availability = Gauge(
    'app_availability',
    'Application availability percentage',
    ['service']
)

app_slo_error_budget_remaining = Gauge(
    'app_slo_error_budget_remaining',
    'Remaining error budget percentage',
    ['service', 'slo_window']
)

# Custom Business Metrics
app_feature_usage = Counter(
    'app_feature_usage_total',
    'Feature usage count',
    ['feature', 'user_tier']
)

app_api_rate_limit_remaining = Gauge(
    'app_api_rate_limit_remaining',
    'API rate limit remaining for user',
    ['user_id', 'api_key']
)

# Application Info
app_info = Info(
    'app',
    'Application information'
)

app_build_info = Info(
    'app_build',
    'Application build information'
)

# Application Status
app_status = Enum(
    'app_status',
    'Application status',
    states=['starting', 'healthy', 'degraded', 'unhealthy']
)


# =============================================================================
# Metric Collection Logic
# =============================================================================

class ApplicationMetricsCollector:
    """Collects application-specific metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.last_collection_time = datetime.now()

        # Set static info metrics
        app_info.info({
            'version': os.getenv('APP_VERSION', '1.0.0'),
            'environment': os.getenv('ENVIRONMENT', 'production'),
            'region': os.getenv('AWS_REGION', 'us-east-1')
        })

        app_build_info.info({
            'git_commit': os.getenv('GIT_COMMIT', 'unknown'),
            'build_date': os.getenv('BUILD_DATE', datetime.now().isoformat()),
            'go_version': 'N/A'
        })

        # Set initial status
        app_status.state('healthy')

        logger.info("Metrics collector initialized")

    def collect_business_metrics(self):
        """Collect business-related metrics."""
        # Simulate active users
        app_active_users.labels(user_type='free').set(random.randint(100, 500))
        app_active_users.labels(user_type='premium').set(random.randint(50, 200))
        app_active_users.labels(user_type='enterprise').set(random.randint(10, 50))

        # Simulate transactions
        if random.random() > 0.7:
            app_transactions_total.labels(
                type='purchase',
                status='completed'
            ).inc(random.randint(1, 5))

        # Simulate revenue
        if random.random() > 0.8:
            revenue = round(random.uniform(10.0, 500.0), 2)
            app_revenue_total.labels(
                product='subscription',
                region='us-east-1'
            ).inc(revenue)

    def collect_performance_metrics(self):
        """Collect performance metrics."""
        # Simulate request metrics
        endpoints = ['/api/users', '/api/products', '/api/orders']
        methods = ['GET', 'POST']

        for endpoint in endpoints:
            for method in methods:
                if random.random() > 0.5:
                    # Request count
                    status = '200' if random.random() > 0.1 else '500'
                    app_requests_total.labels(
                        method=method,
                        endpoint=endpoint,
                        status=status
                    ).inc()

                    # Request duration
                    duration = random.uniform(0.01, 2.0)
                    app_request_duration_seconds.labels(
                        method=method,
                        endpoint=endpoint
                    ).observe(duration)

                    # Request/response sizes
                    app_request_size_bytes.labels(
                        method=method,
                        endpoint=endpoint
                    ).observe(random.randint(100, 10000))

                    app_response_size_bytes.labels(
                        method=method,
                        endpoint=endpoint
                    ).observe(random.randint(500, 50000))

    def collect_database_metrics(self):
        """Collect database metrics."""
        # Active connections
        app_db_connections_active.labels(
            pool='primary',
            database='postgres'
        ).set(random.randint(5, 50))

        app_db_connections_active.labels(
            pool='replica',
            database='postgres'
        ).set(random.randint(3, 30))

        # Query durations
        if random.random() > 0.3:
            query_types = ['SELECT', 'INSERT', 'UPDATE']
            tables = ['users', 'orders', 'products']

            for query_type in query_types:
                for table in tables:
                    if random.random() > 0.5:
                        duration = random.uniform(0.001, 0.5)
                        app_db_query_duration_seconds.labels(
                            query_type=query_type,
                            table=table
                        ).observe(duration)

    def collect_cache_metrics(self):
        """Collect cache metrics."""
        caches = ['redis', 'memcached']

        for cache in caches:
            # Hits and misses
            if random.random() > 0.2:
                app_cache_hits_total.labels(cache=cache).inc(random.randint(1, 10))

            if random.random() > 0.7:
                app_cache_misses_total.labels(cache=cache).inc()

            # Cache size
            app_cache_size_bytes.labels(cache=cache).set(
                random.randint(1000000, 10000000)
            )

    def collect_queue_metrics(self):
        """Collect queue metrics."""
        queues = ['email', 'notifications', 'analytics']

        for queue in queues:
            # Queue depth
            app_queue_depth.labels(queue=queue).set(random.randint(0, 100))

            # Processing time
            if random.random() > 0.5:
                duration = random.uniform(0.1, 10.0)
                app_queue_processing_duration_seconds.labels(
                    queue=queue
                ).observe(duration)

    def collect_error_metrics(self):
        """Collect error metrics."""
        # Simulate errors
        if random.random() > 0.9:
            error_types = ['validation', 'timeout', 'server_error']
            severities = ['warning', 'error', 'critical']

            error_type = random.choice(error_types)
            severity = random.choice(severities)

            app_errors_total.labels(
                error_type=error_type,
                severity=severity
            ).inc()

        # Error rate (calculated metric)
        app_error_rate.labels(window='1m').set(random.uniform(0, 0.05))

    def collect_slo_metrics(self):
        """Collect SLO-related metrics."""
        services = ['api', 'web', 'workers']

        for service in services:
            # Availability (99.9% target)
            availability = random.uniform(99.5, 100.0)
            app_availability.labels(service=service).set(availability)

            # Error budget
            for window in ['7d', '30d']:
                budget = random.uniform(80, 100)
                app_slo_error_budget_remaining.labels(
                    service=service,
                    slo_window=window
                ).set(budget)

    def collect_feature_metrics(self):
        """Collect feature usage metrics."""
        features = ['dashboard', 'reports', 'api', 'export']
        tiers = ['free', 'premium', 'enterprise']

        for feature in features:
            for tier in tiers:
                if random.random() > 0.5:
                    app_feature_usage.labels(
                        feature=feature,
                        user_tier=tier
                    ).inc()

    def collect_all_metrics(self):
        """Collect all application metrics."""
        try:
            logger.info("Starting metric collection...")

            self.collect_business_metrics()
            self.collect_performance_metrics()
            self.collect_database_metrics()
            self.collect_cache_metrics()
            self.collect_queue_metrics()
            self.collect_error_metrics()
            self.collect_slo_metrics()
            self.collect_feature_metrics()

            self.last_collection_time = datetime.now()

            logger.info("Metric collection completed")

        except Exception as e:
            logger.error(f"Error during metric collection: {e}")
            app_status.state('degraded')


# =============================================================================
# Main Application
# =============================================================================

def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description='Custom Application Metrics Exporter for Prometheus'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port to expose metrics on (default: 8000)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=15,
        help='Metric collection interval in seconds (default: 15)'
    )

    args = parser.parse_args()

    logger.info(f"Starting Application Metrics Exporter on port {args.port}")
    logger.info(f"Collection interval: {args.interval} seconds")

    # Start HTTP server for metrics
    start_http_server(args.port)
    logger.info(f"Metrics server started on http://localhost:{args.port}/metrics")

    # Initialize collector
    collector = ApplicationMetricsCollector()

    # Collection loop
    while True:
        try:
            collector.collect_all_metrics()
            time.sleep(args.interval)

        except KeyboardInterrupt:
            logger.info("Shutting down...")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(args.interval)


if __name__ == '__main__':
    main()
