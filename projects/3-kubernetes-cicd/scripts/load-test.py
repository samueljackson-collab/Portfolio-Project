#!/usr/bin/env python3
"""
Load Test Script for K8s CI/CD Demo Application

This script uses Locust to simulate traffic and test the application
under load. It can be run standalone or integrated into CI/CD pipelines.

Usage:
    # Run with web UI (default)
    locust -f load-test.py --host=http://localhost:8080

    # Run headless for CI/CD
    locust -f load-test.py --host=http://localhost:8080 \
           --headless -u 100 -r 10 --run-time 60s

    # Run as standalone script
    python load-test.py --host http://localhost:8080 --users 50 --duration 30

Requirements:
    pip install locust requests
"""

import argparse
import json
import random
import sys
import time
from datetime import datetime

try:
    from locust import HttpUser, task, between, events
    from locust.env import Environment
    from locust.stats import stats_printer, stats_history
    from locust.log import setup_logging
    LOCUST_AVAILABLE = True
except ImportError:
    LOCUST_AVAILABLE = False

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


class K8sCICDUser(HttpUser):
    """Simulated user for load testing the K8s CI/CD demo app."""

    # Wait between 1-3 seconds between tasks
    wait_time = between(1, 3)

    def on_start(self):
        """Called when a user starts."""
        self.task_ids = []

    @task(10)
    def health_check(self):
        """Check health endpoint (most common request)."""
        self.client.get("/health")

    @task(8)
    def ready_check(self):
        """Check readiness endpoint."""
        self.client.get("/ready")

    @task(5)
    def get_status(self):
        """Get application status."""
        self.client.get("/api/v1/status")

    @task(3)
    def get_config(self):
        """Get application config."""
        self.client.get("/api/v1/config")

    @task(2)
    def get_info(self):
        """Get application info."""
        self.client.get("/api/info")

    @task(2)
    def get_home(self):
        """Get home page."""
        self.client.get("/")

    @task(2)
    def get_metrics(self):
        """Get Prometheus metrics."""
        self.client.get("/metrics")

    @task(3)
    def echo_request(self):
        """Send echo request."""
        data = {
            "message": f"Load test message {random.randint(1, 1000)}",
            "timestamp": datetime.utcnow().isoformat()
        }
        self.client.post("/api/echo", json=data)

    @task(1)
    def create_task(self):
        """Create a new task (database operation)."""
        data = {
            "title": f"Load test task {random.randint(1, 10000)}",
            "description": "Created during load testing",
            "priority": random.choice(["low", "medium", "high"])
        }
        response = self.client.post("/api/v1/tasks", json=data)
        if response.status_code == 201:
            result = response.json()
            if 'task' in result and 'id' in result['task']:
                self.task_ids.append(result['task']['id'])

    @task(1)
    def list_tasks(self):
        """List all tasks."""
        self.client.get("/api/v1/tasks")

    @task(1)
    def get_random_task(self):
        """Get a random task if we have any."""
        if self.task_ids:
            task_id = random.choice(self.task_ids)
            self.client.get(f"/api/v1/tasks/{task_id}")


class SimpleLoadTester:
    """Simple load tester for environments without Locust."""

    def __init__(self, host: str, users: int = 10, duration: int = 30):
        self.host = host.rstrip('/')
        self.users = users
        self.duration = duration
        self.results = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_time': 0,
            'min_response_time': float('inf'),
            'max_response_time': 0,
            'errors': []
        }

    def make_request(self, endpoint: str, method: str = 'GET', data: dict = None) -> dict:
        """Make a single HTTP request."""
        url = f"{self.host}{endpoint}"
        start_time = time.time()

        try:
            if method == 'GET':
                response = requests.get(url, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=10)
            else:
                response = requests.request(method, url, json=data, timeout=10)

            elapsed = time.time() - start_time

            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'elapsed': elapsed,
                'error': None
            }
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                'success': False,
                'status_code': 0,
                'elapsed': elapsed,
                'error': str(e)
            }

    def user_simulation(self, user_id: int):
        """Simulate a single user making requests."""
        endpoints = [
            ('/health', 'GET', None),
            ('/ready', 'GET', None),
            ('/api/v1/status', 'GET', None),
            ('/api/v1/config', 'GET', None),
            ('/', 'GET', None),
            ('/api/info', 'GET', None),
            ('/metrics', 'GET', None),
            ('/api/echo', 'POST', {'test': f'user_{user_id}'}),
        ]

        user_results = []
        start_time = time.time()

        while time.time() - start_time < self.duration:
            endpoint, method, data = random.choice(endpoints)
            result = self.make_request(endpoint, method, data)
            user_results.append(result)
            time.sleep(random.uniform(0.5, 2.0))

        return user_results

    def run(self):
        """Run the load test."""
        print(f"\n{'='*60}")
        print(f"  Simple Load Test")
        print(f"{'='*60}")
        print(f"Host: {self.host}")
        print(f"Users: {self.users}")
        print(f"Duration: {self.duration}s")
        print(f"Started: {datetime.utcnow().isoformat()}")
        print()

        all_results = []

        with ThreadPoolExecutor(max_workers=self.users) as executor:
            futures = [
                executor.submit(self.user_simulation, i)
                for i in range(self.users)
            ]

            for future in as_completed(futures):
                try:
                    results = future.result()
                    all_results.extend(results)
                except Exception as e:
                    print(f"Error in user simulation: {e}")

        # Calculate statistics
        for result in all_results:
            self.results['total_requests'] += 1
            self.results['total_time'] += result['elapsed']

            if result['success']:
                self.results['successful_requests'] += 1
            else:
                self.results['failed_requests'] += 1
                if result['error']:
                    self.results['errors'].append(result['error'])

            self.results['min_response_time'] = min(
                self.results['min_response_time'],
                result['elapsed']
            )
            self.results['max_response_time'] = max(
                self.results['max_response_time'],
                result['elapsed']
            )

        # Print results
        self.print_results()

        return self.results['failed_requests'] == 0

    def print_results(self):
        """Print load test results."""
        total = self.results['total_requests']
        success = self.results['successful_requests']
        failed = self.results['failed_requests']
        avg_time = self.results['total_time'] / total if total > 0 else 0

        print(f"\n{'='*60}")
        print(f"  Load Test Results")
        print(f"{'='*60}")
        print(f"Total Requests:     {total}")
        print(f"Successful:         {success} ({success/total*100:.1f}%)" if total > 0 else "Successful: 0")
        print(f"Failed:             {failed} ({failed/total*100:.1f}%)" if total > 0 else "Failed: 0")
        print(f"Requests/second:    {total/self.duration:.2f}")
        print()
        print(f"Response Times:")
        print(f"  Min:              {self.results['min_response_time']*1000:.2f}ms")
        print(f"  Max:              {self.results['max_response_time']*1000:.2f}ms")
        print(f"  Avg:              {avg_time*1000:.2f}ms")
        print()

        if self.results['errors']:
            print(f"Errors ({len(set(self.results['errors']))}):")
            for error in set(self.results['errors']):
                print(f"  - {error}")

        print()
        if failed == 0:
            print("\033[92mLOAD TEST PASSED\033[0m")
        else:
            print("\033[91mLOAD TEST FAILED\033[0m")


def main():
    """Main entry point for standalone execution."""
    parser = argparse.ArgumentParser(description='Load test for K8s CI/CD demo app')
    parser.add_argument('--host', required=True, help='Target host URL')
    parser.add_argument('--users', type=int, default=10, help='Number of concurrent users')
    parser.add_argument('--duration', type=int, default=30, help='Test duration in seconds')
    parser.add_argument('--use-locust', action='store_true', help='Use Locust if available')

    args = parser.parse_args()

    if args.use_locust and LOCUST_AVAILABLE:
        print("Running with Locust...")
        print(f"Start Locust with: locust -f {__file__} --host={args.host}")
        print("Or run headless:")
        print(f"  locust -f {__file__} --host={args.host} --headless -u {args.users} --run-time {args.duration}s")
    else:
        tester = SimpleLoadTester(
            host=args.host,
            users=args.users,
            duration=args.duration
        )
        success = tester.run()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
