"""
Unit tests for Prometheus configuration validation.

Tests verify:
- YAML syntax is valid
- All required fields are present
- Scrape configs are properly formatted
- Alert rules are valid
"""

import json
import os
import tempfile
import subprocess
import yaml
import pytest


class TestPrometheusConfig:
    """Test Prometheus configuration file."""

    @pytest.fixture
    def config_path(self):
        """Return path to prometheus.yml config file."""
        return os.path.join(
            os.path.dirname(__file__),
            "../../config/prometheus.yml"
        )

    @pytest.fixture
    def alerts_path(self):
        """Return path to alerts.yml config file."""
        return os.path.join(
            os.path.dirname(__file__),
            "../../config/alerts.yml"
        )

    def test_prometheus_config_exists(self, config_path):
        """Test that prometheus.yml exists."""
        assert os.path.exists(config_path), f"Config file not found: {config_path}"

    def test_prometheus_config_valid_yaml(self, config_path):
        """Test that prometheus.yml is valid YAML."""
        try:
            with open(config_path, "r") as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML in prometheus.yml: {e}")

    def test_prometheus_config_has_global_section(self, config_path):
        """Test that global configuration section exists."""
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        assert "global" in config, "Missing 'global' section in prometheus.yml"
        assert "scrape_interval" in config["global"]
        assert "evaluation_interval" in config["global"]

    def test_prometheus_config_has_alerting_section(self, config_path):
        """Test that alerting configuration exists."""
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        assert "alerting" in config, "Missing 'alerting' section"
        assert "alertmanagers" in config["alerting"]
        assert len(config["alerting"]["alertmanagers"]) > 0

    def test_prometheus_config_has_scrape_configs(self, config_path):
        """Test that scrape_configs exist."""
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        assert "scrape_configs" in config, "Missing 'scrape_configs' section"
        assert len(config["scrape_configs"]) > 0, "No scrape configs defined"

    def test_prometheus_scrape_configs_have_job_names(self, config_path):
        """Test that all scrape configs have unique job names."""
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        job_names = []
        for scrape_config in config["scrape_configs"]:
            assert "job_name" in scrape_config, "Scrape config missing job_name"
            job_names.append(scrape_config["job_name"])

        # Check for duplicates
        duplicates = [name for name in job_names if job_names.count(name) > 1]
        assert len(duplicates) == 0, f"Duplicate job names found: {duplicates}"

    def test_prometheus_scrape_configs_have_static_configs(self, config_path):
        """Test that scrape configs have static_configs or service discovery."""
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        for scrape_config in config["scrape_configs"]:
            job_name = scrape_config.get("job_name")
            # Each config should have at least one discovery method
            has_static = "static_configs" in scrape_config
            has_sd = any(key in scrape_config for key in [
                "consul_sd_configs",
                "file_sd_configs",
                "ec2_sd_configs",
                "kubernetes_sd_configs"
            ])
            assert has_static or has_sd, \
                f"Scrape config '{job_name}' missing static_configs or service discovery"

    def test_prometheus_required_scrape_targets(self, config_path):
        """Test that required scrape targets are configured."""
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        job_names = [s.get("job_name") for s in config["scrape_configs"]]

        required_jobs = [
            "prometheus",  # Self-monitoring
            "node-exporter",  # Infrastructure metrics
            "backend-api",  # Backend service metrics
            "alertmanager"  # Alert manager
        ]

        for required in required_jobs:
            assert required in job_names, \
                f"Required scrape config '{required}' not found in prometheus.yml"

    def test_prometheus_optional_scrape_targets(self, config_path):
        """Test that optional scrape targets are present."""
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        job_names = [s.get("job_name") for s in config["scrape_configs"]]

        optional_jobs = [
            "frontend-app",  # Frontend service metrics
            "rds-metrics",  # RDS database metrics
            "aws-cloudwatch"  # CloudWatch metrics
        ]

        for optional in optional_jobs:
            assert optional in job_names, \
                f"Optional scrape config '{optional}' not found in prometheus.yml"

    def test_prometheus_scrape_intervals_are_valid(self, config_path):
        """Test that scrape intervals are valid duration strings."""
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        valid_intervals = ["5s", "10s", "15s", "30s", "60s", "120s", "5m", "1m"]

        for scrape_config in config["scrape_configs"]:
            interval = scrape_config.get("scrape_interval", config["global"]["scrape_interval"])
            assert interval in valid_intervals or interval is None, \
                f"Invalid scrape_interval '{interval}' in {scrape_config.get('job_name')}"

    def test_prometheus_rule_files_exist(self, config_path, alerts_path):
        """Test that rule files referenced in prometheus.yml exist."""
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        rule_files = config.get("rule_files", [])
        assert len(rule_files) > 0, "No rule files configured"

        # At least one rule file should exist
        assert os.path.exists(alerts_path), f"Alert rules file not found: {alerts_path}"

    def test_prometheus_labels_in_scrape_configs(self, config_path):
        """Test that important labels are present in scrape configs."""
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        for scrape_config in config["scrape_configs"]:
            job_name = scrape_config.get("job_name")
            static_configs = scrape_config.get("static_configs", [])

            if static_configs:
                for static_config in static_configs:
                    labels = static_config.get("labels", {})
                    # Important labels should be present
                    assert "service" in labels or "job" in labels, \
                        f"Scrape config '{job_name}' missing service/job label"


class TestAlertRules:
    """Test alert rules configuration."""

    @pytest.fixture
    def alerts_path(self):
        """Return path to alerts.yml config file."""
        return os.path.join(
            os.path.dirname(__file__),
            "../../config/alerts.yml"
        )

    def test_alerts_file_exists(self, alerts_path):
        """Test that alerts.yml exists."""
        assert os.path.exists(alerts_path), f"Alerts file not found: {alerts_path}"

    def test_alerts_valid_yaml(self, alerts_path):
        """Test that alerts.yml is valid YAML."""
        try:
            with open(alerts_path, "r") as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(f"Invalid YAML in alerts.yml: {e}")

    def test_alerts_has_groups(self, alerts_path):
        """Test that alerts.yml has alert groups."""
        with open(alerts_path, "r") as f:
            alerts = yaml.safe_load(f)

        assert "groups" in alerts, "Missing 'groups' section in alerts.yml"
        assert len(alerts["groups"]) > 0, "No alert groups defined"

    def test_alert_groups_have_names(self, alerts_path):
        """Test that all alert groups have names."""
        with open(alerts_path, "r") as f:
            alerts = yaml.safe_load(f)

        for group in alerts["groups"]:
            assert "name" in group, "Alert group missing 'name'"
            assert "rules" in group, f"Alert group '{group.get('name')}' missing 'rules'"

    def test_alert_rules_have_required_fields(self, alerts_path):
        """Test that all alert rules have required fields."""
        with open(alerts_path, "r") as f:
            alerts = yaml.safe_load(f)

        required_fields = ["alert", "expr", "for", "labels", "annotations"]

        for group in alerts["groups"]:
            for rule in group.get("rules", []):
                alert_name = rule.get("alert", "unknown")
                for field in required_fields:
                    assert field in rule, \
                        f"Alert '{alert_name}' missing required field '{field}'"

    def test_alert_rules_have_severity(self, alerts_path):
        """Test that all alert rules have a severity label."""
        with open(alerts_path, "r") as f:
            alerts = yaml.safe_load(f)

        valid_severities = ["critical", "warning", "info"]

        for group in alerts["groups"]:
            for rule in group.get("rules", []):
                alert_name = rule.get("alert")
                severity = rule.get("labels", {}).get("severity")
                assert severity is not None, \
                    f"Alert '{alert_name}' missing severity label"
                assert severity in valid_severities, \
                    f"Alert '{alert_name}' has invalid severity: {severity}"

    def test_alert_rules_have_category(self, alerts_path):
        """Test that all alert rules have a category label."""
        with open(alerts_path, "r") as f:
            alerts = yaml.safe_load(f)

        valid_categories = [
            "infrastructure", "application", "database", "slo", "monitoring"
        ]

        for group in alerts["groups"]:
            for rule in group.get("rules", []):
                alert_name = rule.get("alert")
                category = rule.get("labels", {}).get("category")
                assert category is not None, \
                    f"Alert '{alert_name}' missing category label"
                assert category in valid_categories, \
                    f"Alert '{alert_name}' has invalid category: {category}"

    def test_alert_annotations_have_summary(self, alerts_path):
        """Test that alert annotations have summary."""
        with open(alerts_path, "r") as f:
            alerts = yaml.safe_load(f)

        for group in alerts["groups"]:
            for rule in group.get("rules", []):
                alert_name = rule.get("alert")
                summary = rule.get("annotations", {}).get("summary")
                assert summary is not None, \
                    f"Alert '{alert_name}' missing summary annotation"

    def test_alert_annotations_have_description(self, alerts_path):
        """Test that alert annotations have description."""
        with open(alerts_path, "r") as f:
            alerts = yaml.safe_load(f)

        for group in alerts["groups"]:
            for rule in group.get("rules", []):
                alert_name = rule.get("alert")
                description = rule.get("annotations", {}).get("description")
                assert description is not None, \
                    f"Alert '{alert_name}' missing description annotation"

    def test_required_alerts_exist(self, alerts_path):
        """Test that required alert rules exist."""
        with open(alerts_path, "r") as f:
            alerts = yaml.safe_load(f)

        alert_names = []
        for group in alerts["groups"]:
            for rule in group.get("rules", []):
                alert_names.append(rule.get("alert"))

        required_alerts = [
            "InstanceDown",
            "HighCPUUsage",
            "HighMemoryUsage",
            "HighErrorRate",
            "ServiceDown",
            "RDSConnectionPoolExhausted",
            "SlowResponseTime"
        ]

        for required in required_alerts:
            assert required in alert_names, \
                f"Required alert '{required}' not found in alerts.yml"

    def test_alert_expressions_are_not_empty(self, alerts_path):
        """Test that alert expressions are not empty."""
        with open(alerts_path, "r") as f:
            alerts = yaml.safe_load(f)

        for group in alerts["groups"]:
            for rule in group.get("rules", []):
                alert_name = rule.get("alert")
                expr = rule.get("expr", "").strip()
                assert len(expr) > 0, \
                    f"Alert '{alert_name}' has empty expression"

    def test_alert_for_durations_are_valid(self, alerts_path):
        """Test that alert 'for' durations are valid."""
        with open(alerts_path, "r") as f:
            alerts = yaml.safe_load(f)

        for group in alerts["groups"]:
            for rule in group.get("rules", []):
                alert_name = rule.get("alert")
                for_duration = rule.get("for", "1m")
                # Simple check: should contain 's', 'm', or 'h'
                assert any(unit in str(for_duration) for unit in ['s', 'm', 'h']), \
                    f"Alert '{alert_name}' has invalid 'for' duration: {for_duration}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
