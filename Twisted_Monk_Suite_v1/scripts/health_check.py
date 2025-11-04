#!/usr/bin/env python3
"""
Twisted Monk Suite - Health Check Script

Comprehensive health check for all system components.
Can be run as a standalone script or imported as a module.
"""

import sys
import os
import time
import json
import argparse
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    import requests
except ImportError:
    print("Error: requests library not installed. Run: pip install requests")
    sys.exit(1)


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class CheckResult:
    """Result of a health check."""
    name: str
    status: HealthStatus
    message: str
    response_time_ms: float = 0.0
    details: Dict = None


class HealthChecker:
    """Performs health checks on Twisted Monk Suite components."""
    
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 5):
        """
        Initialize health checker.
        
        Args:
            base_url: Base URL of the API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.results: List[CheckResult] = []
    
    def check_api_health(self) -> CheckResult:
        """Check API health endpoint."""
        try:
            start = time.time()
            response = requests.get(
                f"{self.base_url}/health",
                timeout=self.timeout
            )
            response_time = (time.time() - start) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                # Check Redis connectivity
                redis_connected = data.get('redis_connected', False)
                
                if redis_connected:
                    status = HealthStatus.HEALTHY
                    message = "API is healthy and Redis is connected"
                else:
                    status = HealthStatus.DEGRADED
                    message = "API is healthy but Redis is not connected"
                
                return CheckResult(
                    name="API Health",
                    status=status,
                    message=message,
                    response_time_ms=response_time,
                    details=data
                )
            else:
                return CheckResult(
                    name="API Health",
                    status=HealthStatus.UNHEALTHY,
                    message=f"API returned status code {response.status_code}",
                    response_time_ms=response_time
                )
        except requests.exceptions.Timeout:
            return CheckResult(
                name="API Health",
                status=HealthStatus.UNHEALTHY,
                message="API health check timed out"
            )
        except requests.exceptions.ConnectionError:
            return CheckResult(
                name="API Health",
                status=HealthStatus.UNHEALTHY,
                message="Cannot connect to API"
            )
        except Exception as e:
            return CheckResult(
                name="API Health",
                status=HealthStatus.UNHEALTHY,
                message=f"Error: {str(e)}"
            )
    
    def check_api_endpoints(self) -> CheckResult:
        """Check critical API endpoints."""
        endpoints = [
            "/",
            "/api/v1/inventory/PROD-123",
            "/api/v1/bundles/PROD-123",
        ]
        
        failed_endpoints = []
        total_time = 0
        
        for endpoint in endpoints:
            try:
                start = time.time()
                response = requests.get(
                    f"{self.base_url}{endpoint}",
                    timeout=self.timeout
                )
                total_time += (time.time() - start) * 1000
                
                if response.status_code not in [200, 404]:
                    failed_endpoints.append(f"{endpoint} ({response.status_code})")
            except Exception as e:
                failed_endpoints.append(f"{endpoint} ({str(e)})")
        
        if not failed_endpoints:
            return CheckResult(
                name="API Endpoints",
                status=HealthStatus.HEALTHY,
                message=f"All {len(endpoints)} endpoints accessible",
                response_time_ms=total_time / len(endpoints)
            )
        else:
            return CheckResult(
                name="API Endpoints",
                status=HealthStatus.DEGRADED,
                message=f"{len(failed_endpoints)} endpoint(s) failed",
                details={"failed": failed_endpoints}
            )
    
    def check_response_time(self) -> CheckResult:
        """Check API response time performance."""
        try:
            samples = 3
            times = []
            
            for _ in range(samples):
                start = time.time()
                response = requests.get(
                    f"{self.base_url}/health",
                    timeout=self.timeout
                )
                times.append((time.time() - start) * 1000)
                
                if response.status_code != 200:
                    break
            
            avg_time = sum(times) / len(times)
            
            if avg_time < 100:
                status = HealthStatus.HEALTHY
                message = f"Excellent response time: {avg_time:.0f}ms"
            elif avg_time < 500:
                status = HealthStatus.HEALTHY
                message = f"Good response time: {avg_time:.0f}ms"
            elif avg_time < 1000:
                status = HealthStatus.DEGRADED
                message = f"Slow response time: {avg_time:.0f}ms"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Very slow response time: {avg_time:.0f}ms"
            
            return CheckResult(
                name="Response Time",
                status=status,
                message=message,
                response_time_ms=avg_time,
                details={"samples": times}
            )
        except Exception as e:
            return CheckResult(
                name="Response Time",
                status=HealthStatus.UNHEALTHY,
                message=f"Error measuring response time: {str(e)}"
            )
    
    def check_lead_time_api(self) -> CheckResult:
        """Check lead time calculation endpoint."""
        try:
            payload = {
                "supplier_id": "SUP001",
                "product_id": "PROD-123",
                "quantity": 50
            }
            
            start = time.time()
            response = requests.post(
                f"{self.base_url}/api/v1/lead-time",
                json=payload,
                timeout=self.timeout
            )
            response_time = (time.time() - start) * 1000
            
            if response.status_code == 200:
                data = response.json()
                
                # Validate response structure
                required_fields = ['supplier_id', 'product_id', 'estimated_days', 'confidence']
                missing_fields = [f for f in required_fields if f not in data]
                
                if not missing_fields:
                    return CheckResult(
                        name="Lead Time API",
                        status=HealthStatus.HEALTHY,
                        message="Lead time calculation working correctly",
                        response_time_ms=response_time
                    )
                else:
                    return CheckResult(
                        name="Lead Time API",
                        status=HealthStatus.DEGRADED,
                        message=f"Response missing fields: {missing_fields}",
                        response_time_ms=response_time
                    )
            else:
                return CheckResult(
                    name="Lead Time API",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Endpoint returned status {response.status_code}",
                    response_time_ms=response_time
                )
        except Exception as e:
            return CheckResult(
                name="Lead Time API",
                status=HealthStatus.UNHEALTHY,
                message=f"Error: {str(e)}"
            )
    
    def run_all_checks(self) -> List[CheckResult]:
        """Run all health checks."""
        self.results = [
            self.check_api_health(),
            self.check_api_endpoints(),
            self.check_response_time(),
            self.check_lead_time_api(),
        ]
        return self.results
    
    def get_overall_status(self) -> HealthStatus:
        """Get overall system health status."""
        if not self.results:
            return HealthStatus.UNHEALTHY
        
        statuses = [r.status for r in self.results]
        
        if all(s == HealthStatus.HEALTHY for s in statuses):
            return HealthStatus.HEALTHY
        elif any(s == HealthStatus.UNHEALTHY for s in statuses):
            return HealthStatus.UNHEALTHY
        else:
            return HealthStatus.DEGRADED
    
    def print_results(self, verbose: bool = False):
        """Print health check results."""
        print("\n" + "=" * 60)
        print("  Twisted Monk Suite - Health Check Results")
        print("=" * 60 + "\n")
        
        for result in self.results:
            # Status indicator
            if result.status == HealthStatus.HEALTHY:
                indicator = "✓"
                color = "\033[92m"  # Green
            elif result.status == HealthStatus.DEGRADED:
                indicator = "⚠"
                color = "\033[93m"  # Yellow
            else:
                indicator = "✗"
                color = "\033[91m"  # Red
            
            reset = "\033[0m"
            
            print(f"{color}{indicator}{reset} {result.name}: {result.message}")
            
            if result.response_time_ms > 0:
                print(f"  Response time: {result.response_time_ms:.0f}ms")
            
            if verbose and result.details:
                print(f"  Details: {json.dumps(result.details, indent=2)}")
            
            print()
        
        # Overall status
        overall = self.get_overall_status()
        print("=" * 60)
        print(f"Overall Status: {overall.value.upper()}")
        print("=" * 60 + "\n")
    
    def export_json(self) -> str:
        """Export results as JSON."""
        output = {
            "timestamp": time.time(),
            "overall_status": self.get_overall_status().value,
            "checks": [
                {
                    "name": r.name,
                    "status": r.status.value,
                    "message": r.message,
                    "response_time_ms": r.response_time_ms,
                    "details": r.details
                }
                for r in self.results
            ]
        }
        return json.dumps(output, indent=2)


def main():
    """Main entry point for health check script."""
    parser = argparse.ArgumentParser(
        description="Health check for Twisted Monk Suite"
    )
    parser.add_argument(
        "--url",
        default=os.getenv("API_URL", "http://localhost:8000"),
        help="Base URL of the API (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=5,
        help="Request timeout in seconds (default: 5)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output with details"
    )
    
    args = parser.parse_args()
    
    # Run health checks
    checker = HealthChecker(base_url=args.url, timeout=args.timeout)
    checker.run_all_checks()
    
    # Output results
    if args.json:
        print(checker.export_json())
    else:
        checker.print_results(verbose=args.verbose)
    
    # Exit with appropriate code
    overall = checker.get_overall_status()
    if overall == HealthStatus.HEALTHY:
        sys.exit(0)
    elif overall == HealthStatus.DEGRADED:
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
