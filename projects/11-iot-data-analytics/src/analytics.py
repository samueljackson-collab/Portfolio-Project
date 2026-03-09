"""Analytics queries and anomaly detection for IoT telemetry data."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple

import psycopg2
import psycopg2.extras

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IoTAnalytics:
    """Analytics for IoT telemetry data stored in TimescaleDB."""

    def __init__(self, postgres_config: Dict[str, Any]):
        """
        Initialize analytics engine.

        Args:
            postgres_config: PostgreSQL connection parameters
        """
        self.postgres_config = postgres_config
        self.db_conn = psycopg2.connect(**postgres_config)
        logger.info("Connected to TimescaleDB for analytics")

    def get_device_latest_readings(self, device_id: str) -> Dict[str, Any]:
        """
        Get latest readings for a device.

        Args:
            device_id: Device identifier

        Returns:
            Latest telemetry readings
        """
        cursor = self.db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(
            """
            SELECT *
            FROM device_telemetry
            WHERE device_id = %s
            ORDER BY time DESC
            LIMIT 1
        """,
            (device_id,),
        )

        result = cursor.fetchone()
        return dict(result) if result else {}

    def get_device_statistics(self, device_id: str, hours: int = 24) -> Dict[str, Any]:
        """
        Get statistical summary for a device.

        Args:
            device_id: Device identifier
            hours: Time window in hours

        Returns:
            Statistical summary
        """
        cursor = self.db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(
            """
            SELECT
                COUNT(*) as reading_count,
                AVG(temperature) as avg_temperature,
                MIN(temperature) as min_temperature,
                MAX(temperature) as max_temperature,
                STDDEV(temperature) as stddev_temperature,
                AVG(humidity) as avg_humidity,
                MIN(humidity) as min_humidity,
                MAX(humidity) as max_humidity,
                AVG(battery) as avg_battery,
                MIN(battery) as min_battery
            FROM device_telemetry
            WHERE device_id = %s
              AND time > NOW() - INTERVAL '%s hours'
        """,
            (device_id, hours),
        )

        result = cursor.fetchone()
        return dict(result) if result else {}

    def get_all_devices_summary(self) -> List[Dict[str, Any]]:
        """
        Get summary for all devices.

        Returns:
            List of device summaries
        """
        cursor = self.db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(
            """
            SELECT
                device_id,
                MAX(time) as last_seen,
                COUNT(*) as total_readings,
                AVG(temperature) as avg_temperature,
                AVG(humidity) as avg_humidity,
                AVG(battery) as avg_battery,
                MIN(battery) as min_battery
            FROM device_telemetry
            WHERE time > NOW() - INTERVAL '24 hours'
            GROUP BY device_id
            ORDER BY last_seen DESC
        """
        )

        return [dict(row) for row in cursor.fetchall()]

    def detect_temperature_anomalies(
        self, threshold_stddev: float = 2.0, hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Detect temperature anomalies using z-score method.

        Args:
            threshold_stddev: Number of standard deviations for anomaly
            hours: Time window in hours

        Returns:
            List of anomalous readings
        """
        cursor = self.db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(
            """
            WITH device_stats AS (
                SELECT
                    device_id,
                    AVG(temperature) as mean_temp,
                    STDDEV(temperature) as stddev_temp
                FROM device_telemetry
                WHERE time > NOW() - INTERVAL '%s hours'
                GROUP BY device_id
            )
            SELECT
                t.time,
                t.device_id,
                t.temperature,
                s.mean_temp,
                s.stddev_temp,
                ABS(t.temperature - s.mean_temp) / NULLIF(s.stddev_temp, 0) as z_score
            FROM device_telemetry t
            JOIN device_stats s ON t.device_id = s.device_id
            WHERE time > NOW() - INTERVAL '%s hours'
              AND ABS(t.temperature - s.mean_temp) > %s * s.stddev_temp
              AND s.stddev_temp > 0
            ORDER BY time DESC
            LIMIT 100
        """,
            (hours, hours, threshold_stddev),
        )

        return [dict(row) for row in cursor.fetchall()]

    def detect_low_battery_devices(
        self, threshold: float = 20.0
    ) -> List[Dict[str, Any]]:
        """
        Find devices with low battery.

        Args:
            threshold: Battery percentage threshold

        Returns:
            List of devices with low battery
        """
        cursor = self.db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(
            """
            SELECT DISTINCT ON (device_id)
                device_id,
                time as last_reading,
                battery,
                firmware_version
            FROM device_telemetry
            WHERE time > NOW() - INTERVAL '1 hour'
              AND battery < %s
            ORDER BY device_id, time DESC
        """,
            (threshold,),
        )

        return [dict(row) for row in cursor.fetchall()]

    def get_inactive_devices(self, hours: int = 1) -> List[str]:
        """
        Find devices that haven't reported recently.

        Args:
            hours: Inactivity threshold in hours

        Returns:
            List of inactive device IDs
        """
        cursor = self.db_conn.cursor()

        # Get all devices that have ever reported
        cursor.execute(
            """
            SELECT DISTINCT device_id
            FROM device_telemetry
        """
        )

        all_devices = {row[0] for row in cursor.fetchall()}

        # Get active devices
        cursor.execute(
            """
            SELECT DISTINCT device_id
            FROM device_telemetry
            WHERE time > NOW() - INTERVAL '%s hours'
        """,
            (hours,),
        )

        active_devices = {row[0] for row in cursor.fetchall()}

        # Return inactive devices
        return list(all_devices - active_devices)

    def get_time_series(
        self,
        device_id: str,
        metric: str = "temperature",
        interval: str = "5 minutes",
        hours: int = 24,
    ) -> List[Dict[str, Any]]:
        """
        Get time-series data for a device metric.

        Args:
            device_id: Device identifier
            metric: Metric name (temperature, humidity, battery)
            interval: Time bucket interval
            hours: Time window in hours

        Returns:
            Time-series data
        """
        cursor = self.db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = f"""
            SELECT
                time_bucket(%s, time) AS bucket,
                AVG({metric}) as avg_value,
                MIN({metric}) as min_value,
                MAX({metric}) as max_value,
                COUNT(*) as reading_count
            FROM device_telemetry
            WHERE device_id = %s
              AND time > NOW() - INTERVAL '%s hours'
            GROUP BY bucket
            ORDER BY bucket DESC
        """

        cursor.execute(query, (interval, device_id, hours))

        return [dict(row) for row in cursor.fetchall()]

    def get_aggregated_metrics(
        self, interval: str = "1 hour", hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get aggregated metrics across all devices.

        Args:
            interval: Time bucket interval
            hours: Time window in hours

        Returns:
            Aggregated metrics
        """
        cursor = self.db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute(
            """
            SELECT
                time_bucket(%s, time) AS bucket,
                COUNT(DISTINCT device_id) as active_devices,
                COUNT(*) as total_readings,
                AVG(temperature) as avg_temperature,
                AVG(humidity) as avg_humidity,
                AVG(battery) as avg_battery
            FROM device_telemetry
            WHERE time > NOW() - INTERVAL '%s hours'
            GROUP BY bucket
            ORDER BY bucket DESC
        """,
            (interval, hours),
        )

        return [dict(row) for row in cursor.fetchall()]

    def close(self):
        """Close database connection."""
        if self.db_conn:
            self.db_conn.close()
            logger.info("Database connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def main():
    """Example usage."""
    import os

    postgres_config = {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "database": os.getenv("POSTGRES_DB", "iot_analytics"),
        "user": os.getenv("POSTGRES_USER", "iot"),
        "password": os.getenv("POSTGRES_PASSWORD", "iot_password"),
    }

    with IoTAnalytics(postgres_config) as analytics:
        # Get all devices summary
        print("\n=== All Devices Summary ===")
        devices = analytics.get_all_devices_summary()
        for device in devices:
            print(f"Device: {device['device_id']}")
            print(f"  Last Seen: {device['last_seen']}")
            print(f"  Avg Temp: {device['avg_temperature']:.2f}°C")
            print(f"  Battery: {device['avg_battery']:.1f}%")
            print()

        # Detect anomalies
        print("\n=== Temperature Anomalies ===")
        anomalies = analytics.detect_temperature_anomalies()
        for anomaly in anomalies[:5]:
            print(f"Device: {anomaly['device_id']}")
            print(f"  Time: {anomaly['time']}")
            print(f"  Temperature: {anomaly['temperature']:.2f}°C")
            print(f"  Z-Score: {anomaly['z_score']:.2f}")
            print()

        # Low battery devices
        print("\n=== Low Battery Devices ===")
        low_battery = analytics.detect_low_battery_devices(threshold=30.0)
        for device in low_battery:
            print(f"Device: {device['device_id']}")
            print(f"  Battery: {device['battery']:.1f}%")
            print()


if __name__ == "__main__":
    main()
