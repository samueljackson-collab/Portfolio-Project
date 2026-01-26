#!/usr/bin/env python3
"""Device provisioning workflow for IoT devices."""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

import psycopg2

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DeviceProvisioner:
    """Manages device provisioning and lifecycle."""

    def __init__(self, db_config: Dict, aws_iot_client=None):
        """
        Initialize device provisioner.

        Args:
            db_config: Database configuration
            aws_iot_client: Optional boto3 IoT client for AWS IoT Core
        """
        self.db_config = db_config
        self.iot_client = aws_iot_client

        # Initialize database
        self._init_database()

        logger.info("Device provisioner initialized")

    def _init_database(self):
        """Initialize database tables for device management."""
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()

        # Create devices table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS devices (
                device_id VARCHAR(50) PRIMARY KEY,
                device_name VARCHAR(100),
                device_type VARCHAR(50),
                manufacturer VARCHAR(100),
                model VARCHAR(100),
                firmware_version VARCHAR(50),
                location VARCHAR(200),
                status VARCHAR(20) DEFAULT 'active',
                provisioned_at TIMESTAMP DEFAULT NOW(),
                last_seen TIMESTAMP,
                metadata JSONB,
                aws_thing_name VARCHAR(100),
                aws_certificate_arn TEXT,
                aws_certificate_id VARCHAR(100)
            )
        """
        )

        # Create device credentials table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS device_credentials (
                credential_id SERIAL PRIMARY KEY,
                device_id VARCHAR(50) REFERENCES devices(device_id),
                credential_type VARCHAR(20),
                public_key TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                expires_at TIMESTAMP,
                revoked BOOLEAN DEFAULT FALSE
            )
        """
        )

        # Create device events table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS device_events (
                event_id SERIAL PRIMARY KEY,
                device_id VARCHAR(50) REFERENCES devices(device_id),
                event_type VARCHAR(50),
                event_data JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """
        )

        conn.commit()
        cursor.close()
        conn.close()

        logger.info("Database initialized")

    def provision_device(
        self,
        device_name: str,
        device_type: str = "sensor",
        manufacturer: str = "IoTSolutions",
        model: str = "SENSOR-X100",
        location: str = "datacenter-1",
        metadata: Optional[Dict] = None,
        create_aws_thing: bool = False,
    ) -> Dict:
        """
        Provision a new IoT device.

        Args:
            device_name: Human-readable device name
            device_type: Type of device
            manufacturer: Device manufacturer
            model: Device model
            location: Physical location
            metadata: Additional metadata
            create_aws_thing: Whether to create AWS IoT Core thing

        Returns:
            Dictionary with device information
        """
        device_id = f"device-{uuid.uuid4().hex[:8]}"

        logger.info(f"Provisioning device: {device_name} (ID: {device_id})")

        # Create AWS IoT Core thing if requested
        aws_info = {}
        if create_aws_thing and self.iot_client:
            aws_info = self._create_aws_thing(device_id, device_name, device_type)

        # Store in database
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO devices (
                device_id, device_name, device_type, manufacturer,
                model, location, metadata, aws_thing_name,
                aws_certificate_arn, aws_certificate_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                device_id,
                device_name,
                device_type,
                manufacturer,
                model,
                location,
                json.dumps(metadata or {}),
                aws_info.get("thing_name"),
                aws_info.get("certificate_arn"),
                aws_info.get("certificate_id"),
            ),
        )

        # Log provisioning event
        cursor.execute(
            """
            INSERT INTO device_events (device_id, event_type, event_data)
            VALUES (%s, %s, %s)
        """,
            (
                device_id,
                "provisioned",
                json.dumps(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "location": location,
                        "aws_enabled": create_aws_thing,
                    }
                ),
            ),
        )

        conn.commit()
        cursor.close()
        conn.close()

        device_info = {
            "device_id": device_id,
            "device_name": device_name,
            "device_type": device_type,
            "manufacturer": manufacturer,
            "model": model,
            "location": location,
            "status": "active",
            "provisioned_at": datetime.now().isoformat(),
            **aws_info,
        }

        logger.info(f"Device provisioned successfully: {device_id}")

        return device_info

    def _create_aws_thing(
        self, device_id: str, device_name: str, device_type: str
    ) -> Dict:
        """
        Create AWS IoT Core thing and certificate.

        Args:
            device_id: Device ID
            device_name: Device name
            device_type: Device type

        Returns:
            Dictionary with AWS IoT Core information
        """
        if not self.iot_client:
            return {}

        try:
            # Create IoT thing
            thing_name = f"iot-{device_id}"
            response = self.iot_client.create_thing(
                thingName=thing_name,
                attributePayload={
                    "attributes": {
                        "device_id": device_id,
                        "device_name": device_name,
                        "device_type": device_type,
                    }
                },
            )

            # Create certificate
            cert_response = self.iot_client.create_keys_and_certificate(
                setAsActive=True
            )

            certificate_arn = cert_response["certificateArn"]
            certificate_id = cert_response["certificateId"]

            # Attach policy to certificate
            policy_name = "iot-device-policy"  # Pre-created policy
            self.iot_client.attach_policy(
                policyName=policy_name, target=certificate_arn
            )

            # Attach certificate to thing
            self.iot_client.attach_thing_principal(
                thingName=thing_name, principal=certificate_arn
            )

            # Save certificate files
            cert_dir = Path(f"certs/{device_id}")
            cert_dir.mkdir(parents=True, exist_ok=True)

            (cert_dir / "certificate.pem").write_text(cert_response["certificatePem"])
            (cert_dir / "private.key").write_text(
                cert_response["keyPair"]["PrivateKey"]
            )
            (cert_dir / "public.key").write_text(cert_response["keyPair"]["PublicKey"])

            logger.info(f"AWS IoT thing created: {thing_name}")

            return {
                "thing_name": thing_name,
                "certificate_arn": certificate_arn,
                "certificate_id": certificate_id,
                "certificate_path": str(cert_dir / "certificate.pem"),
                "private_key_path": str(cert_dir / "private.key"),
            }

        except Exception as e:
            logger.error(f"Error creating AWS thing: {e}")
            return {}

    def decommission_device(self, device_id: str):
        """
        Decommission a device.

        Args:
            device_id: Device ID
        """
        logger.info(f"Decommissioning device: {device_id}")

        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()

        # Update device status
        cursor.execute(
            """
            UPDATE devices
            SET status = 'decommissioned'
            WHERE device_id = %s
        """,
            (device_id,),
        )

        # Log decommissioning event
        cursor.execute(
            """
            INSERT INTO device_events (device_id, event_type, event_data)
            VALUES (%s, %s, %s)
        """,
            (
                device_id,
                "decommissioned",
                json.dumps({"timestamp": datetime.now().isoformat()}),
            ),
        )

        # Revoke credentials
        cursor.execute(
            """
            UPDATE device_credentials
            SET revoked = TRUE
            WHERE device_id = %s AND revoked = FALSE
        """,
            (device_id,),
        )

        conn.commit()
        cursor.close()
        conn.close()

        logger.info(f"Device decommissioned: {device_id}")

    def list_devices(self, status: Optional[str] = None) -> list:
        """
        List all devices.

        Args:
            status: Optional status filter

        Returns:
            List of devices
        """
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()

        if status:
            cursor.execute(
                """
                SELECT device_id, device_name, device_type, location,
                       status, provisioned_at, last_seen
                FROM devices
                WHERE status = %s
                ORDER BY provisioned_at DESC
            """,
                (status,),
            )
        else:
            cursor.execute(
                """
                SELECT device_id, device_name, device_type, location,
                       status, provisioned_at, last_seen
                FROM devices
                ORDER BY provisioned_at DESC
            """
            )

        devices = []
        for row in cursor.fetchall():
            devices.append(
                {
                    "device_id": row[0],
                    "device_name": row[1],
                    "device_type": row[2],
                    "location": row[3],
                    "status": row[4],
                    "provisioned_at": row[5].isoformat() if row[5] else None,
                    "last_seen": row[6].isoformat() if row[6] else None,
                }
            )

        cursor.close()
        conn.close()

        return devices

    def get_device_info(self, device_id: str) -> Optional[Dict]:
        """
        Get detailed device information.

        Args:
            device_id: Device ID

        Returns:
            Device information or None if not found
        """
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT device_id, device_name, device_type, manufacturer,
                   model, location, status, provisioned_at, last_seen,
                   metadata, aws_thing_name
            FROM devices
            WHERE device_id = %s
        """,
            (device_id,),
        )

        row = cursor.fetchone()
        if not row:
            cursor.close()
            conn.close()
            return None

        device_info = {
            "device_id": row[0],
            "device_name": row[1],
            "device_type": row[2],
            "manufacturer": row[3],
            "model": row[4],
            "location": row[5],
            "status": row[6],
            "provisioned_at": row[7].isoformat() if row[7] else None,
            "last_seen": row[8].isoformat() if row[8] else None,
            "metadata": row[9],
            "aws_thing_name": row[10],
        }

        # Get recent events
        cursor.execute(
            """
            SELECT event_type, event_data, created_at
            FROM device_events
            WHERE device_id = %s
            ORDER BY created_at DESC
            LIMIT 10
        """,
            (device_id,),
        )

        events = []
        for event_row in cursor.fetchall():
            events.append(
                {
                    "event_type": event_row[0],
                    "event_data": event_row[1],
                    "created_at": event_row[2].isoformat() if event_row[2] else None,
                }
            )

        device_info["recent_events"] = events

        cursor.close()
        conn.close()

        return device_info


def main():
    """CLI for device provisioning."""
    import argparse

    parser = argparse.ArgumentParser(description="Device Provisioning")
    parser.add_argument(
        "--action", choices=["provision", "list", "info", "decommission"], required=True
    )
    parser.add_argument("--device-name", help="Device name")
    parser.add_argument("--device-type", default="sensor", help="Device type")
    parser.add_argument("--location", default="datacenter-1", help="Device location")
    parser.add_argument("--device-id", help="Device ID")
    parser.add_argument("--status", help="Status filter for list")
    parser.add_argument("--db-host", default="localhost")
    parser.add_argument("--db-port", type=int, default=5432)
    parser.add_argument("--db-name", default="iot_analytics")
    parser.add_argument("--db-user", default="postgres")
    parser.add_argument("--db-password", default="postgres")

    args = parser.parse_args()

    db_config = {
        "host": args.db_host,
        "port": args.db_port,
        "database": args.db_name,
        "user": args.db_user,
        "password": args.db_password,
    }

    provisioner = DeviceProvisioner(db_config)

    if args.action == "provision":
        if not args.device_name:
            print("Error: --device-name required")
            return

        device = provisioner.provision_device(
            device_name=args.device_name,
            device_type=args.device_type,
            location=args.location,
        )

        print("\nDevice provisioned:")
        print(json.dumps(device, indent=2))

    elif args.action == "list":
        devices = provisioner.list_devices(status=args.status)

        print(f"\nDevices ({len(devices)}):")
        for device in devices:
            print(
                f"  {device['device_id']}: {device['device_name']} ({device['status']})"
            )

    elif args.action == "info":
        if not args.device_id:
            print("Error: --device-id required")
            return

        info = provisioner.get_device_info(args.device_id)
        if info:
            print("\nDevice Information:")
            print(json.dumps(info, indent=2))
        else:
            print(f"Device not found: {args.device_id}")

    elif args.action == "decommission":
        if not args.device_id:
            print("Error: --device-id required")
            return

        provisioner.decommission_device(args.device_id)
        print(f"Device decommissioned: {args.device_id}")


if __name__ == "__main__":
    main()
