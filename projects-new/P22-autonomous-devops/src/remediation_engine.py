#!/usr/bin/env python3
"""
Autonomous DevOps Remediation Engine

Detects incidents and automatically remediates common issues.
"""

import time
import requests
import subprocess
from datetime import datetime
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RemediationEngine:
    """Autonomous remediation for common DevOps incidents."""

    def __init__(self, prometheus_url='http://localhost:9090'):
        """Initialize remediation engine."""
        self.prometheus_url = prometheus_url
        self.remediation_history = []

    def query_prometheus(self, query: str) -> Dict:
        """Query Prometheus for metrics."""
        try:
            response = requests.get(
                f"{self.prometheus_url}/api/v1/query",
                params={'query': query}
            )
            return response.json()
        except Exception as e:
            logger.error(f"Prometheus query failed: {e}")
            return {}

    def check_high_cpu(self, threshold=80) -> List[Dict]:
        """Check for high CPU usage."""
        query = f'100 - (avg by (instance) (rate(node_cpu_seconds_total{{mode="idle"}}[5m])) * 100) > {threshold}'
        result = self.query_prometheus(query)

        incidents = []
        if result.get('status') == 'success':
            for item in result['data']['result']:
                instance = item['metric'].get('instance', 'unknown')
                value = float(item['value'][1])
                incidents.append({
                    'type': 'high_cpu',
                    'instance': instance,
                    'value': value,
                    'threshold': threshold
                })

        return incidents

    def check_high_memory(self, threshold=90) -> List[Dict]:
        """Check for high memory usage."""
        query = f'100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) > {threshold}'
        result = self.query_prometheus(query)

        incidents = []
        if result.get('status') == 'success':
            for item in result['data']['result']:
                instance = item['metric'].get('instance', 'unknown')
                value = float(item['value'][1])
                incidents.append({
                    'type': 'high_memory',
                    'instance': instance,
                    'value': value,
                    'threshold': threshold
                })

        return incidents

    def check_failed_health_checks(self) -> List[Dict]:
        """Check for failed application health checks."""
        query = 'up{job=~".*app.*"} == 0'
        result = self.query_prometheus(query)

        incidents = []
        if result.get('status') == 'success':
            for item in result['data']['result']:
                job = item['metric'].get('job', 'unknown')
                instance = item['metric'].get('instance', 'unknown')
                incidents.append({
                    'type': 'failed_health_check',
                    'job': job,
                    'instance': instance
                })

        return incidents

    def check_high_error_rate(self, threshold=5) -> List[Dict]:
        """Check for high HTTP error rates."""
        query = f'rate(http_requests_total{{status=~"5.."}}[5m]) * 100 > {threshold}'
        result = self.query_prometheus(query)

        incidents = []
        if result.get('status') == 'success':
            for item in result['data']['result']:
                service = item['metric'].get('service', 'unknown')
                value = float(item['value'][1])
                incidents.append({
                    'type': 'high_error_rate',
                    'service': service,
                    'value': value,
                    'threshold': threshold
                })

        return incidents

    def remediate_high_cpu(self, incident: Dict) -> bool:
        """Remediate high CPU usage."""
        logger.info(f"Remediating high CPU on {incident['instance']}")

        # Strategy: Restart resource-intensive processes
        try:
            # In production, this would identify and restart specific services
            # For demo, we'll log the action
            logger.info(f"  Action: Restarting services on {incident['instance']}")
            logger.info(f"  CPU usage: {incident['value']:.2f}%")

            # Simulate remediation
            remediation = {
                'timestamp': datetime.now().isoformat(),
                'incident': incident,
                'action': 'restart_services',
                'status': 'simulated'
            }

            self.remediation_history.append(remediation)
            return True
        except Exception as e:
            logger.error(f"Remediation failed: {e}")
            return False

    def remediate_high_memory(self, incident: Dict) -> bool:
        """Remediate high memory usage."""
        logger.info(f"Remediating high memory on {incident['instance']}")

        try:
            # Strategy: Clear caches, restart memory-intensive services
            logger.info(f"  Action: Clearing caches on {incident['instance']}")
            logger.info(f"  Memory usage: {incident['value']:.2f}%")

            remediation = {
                'timestamp': datetime.now().isoformat(),
                'incident': incident,
                'action': 'clear_caches',
                'status': 'simulated'
            }

            self.remediation_history.append(remediation)
            return True
        except Exception as e:
            logger.error(f"Remediation failed: {e}")
            return False

    def remediate_failed_health_check(self, incident: Dict) -> bool:
        """Remediate failed health checks by restarting service."""
        logger.info(f"Remediating failed health check for {incident['job']}")

        try:
            # In Kubernetes, this would use kubectl restart
            # For Docker, use docker restart
            logger.info(f"  Action: Restarting {incident['job']}")

            # Simulate kubectl/docker restart
            command = f"kubectl rollout restart deployment/{incident['job']}"
            logger.info(f"  Command: {command}")

            remediation = {
                'timestamp': datetime.now().isoformat(),
                'incident': incident,
                'action': 'restart_deployment',
                'command': command,
                'status': 'simulated'
            }

            self.remediation_history.append(remediation)
            return True
        except Exception as e:
            logger.error(f"Remediation failed: {e}")
            return False

    def remediate_high_error_rate(self, incident: Dict) -> bool:
        """Remediate high error rates."""
        logger.info(f"Remediating high error rate for {incident['service']}")

        try:
            # Strategy: Scale up service, rollback to previous version
            logger.info(f"  Action: Scaling up {incident['service']}")
            logger.info(f"  Error rate: {incident['value']:.2f}%")

            # In production, check if scaling helps, otherwise rollback
            command = f"kubectl scale deployment/{incident['service']} --replicas=5"
            logger.info(f"  Command: {command}")

            remediation = {
                'timestamp': datetime.now().isoformat(),
                'incident': incident,
                'action': 'scale_up',
                'command': command,
                'status': 'simulated'
            }

            self.remediation_history.append(remediation)
            return True
        except Exception as e:
            logger.error(f"Remediation failed: {e}")
            return False

    def run_once(self):
        """Run a single remediation cycle."""
        logger.info("="*60)
        logger.info("Running remediation cycle...")
        logger.info("="*60)

        # Check for incidents
        incidents = []
        incidents.extend(self.check_high_cpu())
        incidents.extend(self.check_high_memory())
        incidents.extend(self.check_failed_health_checks())
        incidents.extend(self.check_high_error_rate())

        if not incidents:
            logger.info("No incidents detected")
            return

        logger.info(f"Detected {len(incidents)} incident(s)")

        # Remediate incidents
        for incident in incidents:
            incident_type = incident['type']

            if incident_type == 'high_cpu':
                self.remediate_high_cpu(incident)
            elif incident_type == 'high_memory':
                self.remediate_high_memory(incident)
            elif incident_type == 'failed_health_check':
                self.remediate_failed_health_check(incident)
            elif incident_type == 'high_error_rate':
                self.remediate_high_error_rate(incident)

        logger.info(f"Remediation cycle completed")

    def run_continuously(self, interval=60):
        """Run remediation engine continuously."""
        logger.info(f"Starting autonomous remediation engine (interval: {interval}s)")

        try:
            while True:
                self.run_once()
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("\nShutting down remediation engine")
            self.print_summary()

    def print_summary(self):
        """Print remediation summary."""
        logger.info("\n" + "="*60)
        logger.info("REMEDIATION SUMMARY")
        logger.info("="*60)
        logger.info(f"Total remediations: {len(self.remediation_history)}")

        for i, remediation in enumerate(self.remediation_history, 1):
            logger.info(f"\n{i}. {remediation['incident']['type']}")
            logger.info(f"   Timestamp: {remediation['timestamp']}")
            logger.info(f"   Action: {remediation['action']}")
            logger.info(f"   Status: {remediation['status']}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Autonomous DevOps Remediation Engine')
    parser.add_argument('--prometheus-url', default='http://localhost:9090',
                        help='Prometheus server URL')
    parser.add_argument('--interval', type=int, default=60,
                        help='Check interval in seconds')
    parser.add_argument('--once', action='store_true',
                        help='Run once and exit')

    args = parser.parse_args()

    engine = RemediationEngine(prometheus_url=args.prometheus_url)

    if args.once:
        engine.run_once()
    else:
        engine.run_continuously(interval=args.interval)


if __name__ == '__main__':
    main()
