from typing import Callable, Dict, List, Any


class RemediationEngine:
    def __init__(self, prometheus_client: Any):
        self.prometheus_client = prometheus_client

    def query_prometheus(self, query: str) -> Dict:
        """Wrapper to query Prometheus; expects a dict response."""
        return self.prometheus_client.query(query)

    def _query_and_parse_incidents(
        self,
        query: str,
        incident_type: str,
        threshold: int,
        extract_fn: Callable[[Dict, str, int], Dict]
    ) -> List[Dict]:
        """Helper to query Prometheus and parse incidents safely."""
        result = self.query_prometheus(query)
        incidents: List[Dict] = []

        if result.get("status") == "success" and "data" in result and "result" in result.get("data", {}):
            for item in result["data"]["result"]:
                incidents.append(extract_fn(item, incident_type, threshold))

        return incidents

    def check_high_cpu(self, threshold: int = 80) -> List[Dict]:
        query = f'100 - (avg by (instance) (rate(node_cpu_seconds_total{{mode="idle"}}[5m])) * 100) > {threshold}'
        return self._query_and_parse_incidents(
            query,
            "high_cpu",
            threshold,
            lambda item, incident_type, th: {
                "type": incident_type,
                "instance": item["metric"].get("instance", "unknown"),
                "value": float(item["value"][1]),
                "threshold": th,
            },
        )

    def check_high_memory(self, threshold: int = 90) -> List[Dict]:
        query = f'100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) > {threshold}'
        return self._query_and_parse_incidents(
            query,
            "high_memory",
            threshold,
            lambda item, incident_type, th: {
                "type": incident_type,
                "instance": item["metric"].get("instance", "unknown"),
                "value": float(item["value"][1]),
                "threshold": th,
            },
        )

    def check_failed_health_checks(self) -> List[Dict]:
        query = 'up{job=~".*app.*"} == 0'
        return self._query_and_parse_incidents(
            query,
            "failed_health_check",
            threshold=0,
            extract_fn=lambda item, incident_type, th: {
                "type": incident_type,
                "job": item["metric"].get("job", "unknown"),
                "instance": item["metric"].get("instance", "unknown"),
            },
        )

    def check_high_error_rate(self, threshold: int = 5) -> List[Dict]:
        query = f'rate(http_requests_total{{status=~"5.."}}[5m]) * 100 > {threshold}'
        return self._query_and_parse_incidents(
            query,
            "high_error_rate",
            threshold,
            lambda item, incident_type, th: {
                "type": incident_type,
                "service": item["metric"].get("service", "unknown"),
                "value": float(item["value"][1]),
                "threshold": th,
            },
        )
