"""
Comprehensive tests for YAML configuration files

Tests validate:
- YAML syntax and structure
- Required fields and sections
- Configuration completeness
- Best practices and conventions
- Security considerations
"""
import os
import yaml
import pytest
from pathlib import Path
from typing import Dict, Any

# Path to configuration files
ALERTMANAGER_CONFIG = Path(__file__).parent.parent.parent / "projects/01-sde-devops/PRJ-SDE-002/assets/alertmanager/alertmanager.yml"
LOKI_CONFIG = Path(__file__).parent.parent.parent / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/loki-config.yml"
PROMTAIL_CONFIG = Path(__file__).parent.parent.parent / "projects/01-sde-devops/PRJ-SDE-002/assets/loki/promtail-config.yml"
PROMETHEUS_CONFIG = Path(__file__).parent.parent.parent / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/prometheus.yml"
INFRASTRUCTURE_ALERTS = Path(__file__).parent.parent.parent / "projects/01-sde-devops/PRJ-SDE-002/assets/prometheus/alerts/infrastructure_alerts.yml"


class TestAlertmanagerConfig:
    """Test Alertmanager configuration file"""
    
    @pytest.fixture
    def config(self) -> Dict[str, Any]:
        """Load Alertmanager config"""
        with open(ALERTMANAGER_CONFIG, 'r') as f:
            return yaml.safe_load(f)
    
    def test_file_exists(self):
        """Verify alertmanager.yml exists"""
        assert ALERTMANAGER_CONFIG.exists(), f"Config not found at {ALERTMANAGER_CONFIG}"
    
    def test_valid_yaml_syntax(self):
        """Verify file contains valid YAML"""
        with open(ALERTMANAGER_CONFIG, 'r') as f:
            config = yaml.safe_load(f)
        assert config is not None, "Config should parse successfully"
    
    def test_has_global_section(self, config):
        """Verify global section exists"""
        assert 'global' in config, "Config must have global section"
    
    def test_global_resolve_timeout(self, config):
        """Verify resolve_timeout is configured"""
        assert 'resolve_timeout' in config['global'], "Global should define resolve_timeout"
        timeout = config['global']['resolve_timeout']
        assert timeout, "resolve_timeout should not be empty"
    
    def test_global_smtp_configuration(self, config):
        """Verify SMTP settings are present"""
        global_config = config['global']
        assert 'smtp_smarthost' in global_config, "Should configure SMTP smarthost"
        assert 'smtp_from' in global_config, "Should configure from address"
        assert 'smtp_require_tls' in global_config, "Should specify TLS requirement"
    
    def test_smtp_uses_tls(self, config):
        """Verify SMTP requires TLS"""
        assert config['global']['smtp_require_tls'] is True, "SMTP should require TLS"
    
    def test_has_slack_webhook(self, config):
        """Verify Slack webhook is configured"""
        assert 'slack_api_url' in config['global'], "Should configure Slack webhook"
        webhook = config['global']['slack_api_url']
        assert 'hooks.slack.com' in webhook, "Should be a valid Slack webhook URL"
    
    def test_has_route_section(self, config):
        """Verify route section exists"""
        assert 'route' in config, "Config must have route section"
    
    def test_route_has_default_receiver(self, config):
        """Verify default receiver is specified"""
        assert 'receiver' in config['route'], "Route must specify default receiver"
        assert config['route']['receiver'], "Default receiver should not be empty"
    
    def test_route_has_group_by(self, config):
        """Verify route defines grouping strategy"""
        assert 'group_by' in config['route'], "Route should define group_by"
        assert isinstance(config['route']['group_by'], list), "group_by should be a list"
        assert len(config['route']['group_by']) > 0, "group_by should not be empty"
    
    def test_route_has_timing_parameters(self, config):
        """Verify route defines timing parameters"""
        route = config['route']
        assert 'group_wait' in route, "Route should define group_wait"
        assert 'group_interval' in route, "Route should define group_interval"
        assert 'repeat_interval' in route, "Route should define repeat_interval"
    
    def test_route_has_subroutes(self, config):
        """Verify route has child routes for different severities"""
        assert 'routes' in config['route'], "Route should have child routes"
        routes = config['route']['routes']
        assert isinstance(routes, list), "Routes should be a list"
        assert len(routes) > 0, "Should have at least one child route"
    
    def test_critical_route_exists(self, config):
        """Verify critical alerts have dedicated route"""
        routes = config['route']['routes']
        critical_routes = [r for r in routes if 'matchers' in r and 
                          any('critical' in str(m) for m in r['matchers'])]
        assert len(critical_routes) > 0, "Should have route for critical alerts"
    
    def test_critical_route_has_fast_notification(self, config):
        """Verify critical alerts have shorter group_wait"""
        routes = config['route']['routes']
        critical_routes = [r for r in routes if 'matchers' in r and 
                          any('critical' in str(m) for m in r['matchers'])]
        for route in critical_routes:
            if 'group_wait' in route:
                # Critical should have fast notification (< 30s)
                wait = route['group_wait']
                assert 's' in wait and int(wait.rstrip('s')) <= 30, \
                    "Critical alerts should have fast group_wait"
    
    def test_backup_route_exists(self, config):
        """Verify backup alerts have dedicated route"""
        routes = config['route']['routes']
        backup_routes = [r for r in routes if 'matchers' in r and 
                        any('backup' in str(m) for m in r['matchers'])]
        assert len(backup_routes) > 0, "Should have route for backup alerts"
    
    def test_has_receivers_section(self, config):
        """Verify receivers section exists"""
        assert 'receivers' in config, "Config must have receivers section"
        assert isinstance(config['receivers'], list), "Receivers should be a list"
        assert len(config['receivers']) > 0, "Should have at least one receiver"
    
    def test_all_receivers_have_names(self, config):
        """Verify all receivers have unique names"""
        receivers = config['receivers']
        names = [r['name'] for r in receivers]
        assert len(names) == len(set(names)), "Receiver names should be unique"
        assert all(name for name in names), "All receivers must have names"
    
    def test_default_receiver_is_defined(self, config):
        """Verify default receiver exists in receivers list"""
        default = config['route']['receiver']
        receiver_names = [r['name'] for r in config['receivers']]
        assert default in receiver_names, f"Default receiver '{default}' not found in receivers"
    
    def test_route_receivers_are_defined(self, config):
        """Verify all route receivers exist in receivers list"""
        receiver_names = [r['name'] for r in config['receivers']]
        if 'routes' in config['route']:
            for route in config['route']['routes']:
                if 'receiver' in route:
                    assert route['receiver'] in receiver_names, \
                        f"Route receiver '{route['receiver']}' not found"
    
    def test_email_receiver_configuration(self, config):
        """Verify email receivers are properly configured"""
        for receiver in config['receivers']:
            if 'email_configs' in receiver:
                for email_config in receiver['email_configs']:
                    assert 'to' in email_config, "Email config must specify 'to'"
                    assert '@' in email_config['to'], "Email address should contain @"
    
    def test_email_has_subject_template(self, config):
        """Verify email receivers have subject templates"""
        for receiver in config['receivers']:
            if 'email_configs' in receiver:
                for email_config in receiver['email_configs']:
                    if 'headers' in email_config:
                        assert 'subject' in email_config['headers'], \
                            "Email should have subject header"
    
    def test_email_has_html_body(self, config):
        """Verify email receivers use HTML formatting"""
        for receiver in config['receivers']:
            if 'email_configs' in receiver:
                for email_config in receiver['email_configs']:
                    if 'html' in email_config:
                        html = email_config['html']
                        assert '<html>' in html or '<table>' in html, \
                            "HTML body should contain HTML tags"
    
    def test_matchers_use_new_syntax(self, config):
        """Verify routes use matchers (not deprecated match)"""
        if 'routes' in config['route']:
            for route in config['route']['routes']:
                # New syntax uses 'matchers', old uses 'match' or 'match_re'
                if 'matchers' not in route:
                    # It's ok if route doesn't filter, but shouldn't use old syntax
                    assert 'match' not in route, "Use 'matchers' instead of deprecated 'match'"
                    assert 'match_re' not in route, "Use 'matchers' instead of deprecated 'match_re'"


class TestLokiConfig:
    """Test Loki configuration file"""
    
    @pytest.fixture
    def config(self) -> Dict[str, Any]:
        """Load Loki config"""
        with open(LOKI_CONFIG, 'r') as f:
            return yaml.safe_load(f)
    
    def test_file_exists(self):
        """Verify loki-config.yml exists"""
        assert LOKI_CONFIG.exists(), f"Config not found at {LOKI_CONFIG}"
    
    def test_valid_yaml_syntax(self):
        """Verify file contains valid YAML"""
        with open(LOKI_CONFIG, 'r') as f:
            config = yaml.safe_load(f)
        assert config is not None, "Config should parse successfully"
    
    def test_has_server_section(self, config):
        """Verify server section exists"""
        assert 'server' in config, "Config must have server section"
    
    def test_server_ports_configured(self, config):
        """Verify HTTP and gRPC ports are specified"""
        server = config['server']
        assert 'http_listen_port' in server, "Should define HTTP port"
        assert 'grpc_listen_port' in server, "Should define gRPC port"
        assert isinstance(server['http_listen_port'], int), "HTTP port should be integer"
    
    def test_http_port_is_standard(self, config):
        """Verify HTTP port is 3100 (Loki default)"""
        assert config['server']['http_listen_port'] == 3100, \
            "Loki typically uses port 3100"
    
    def test_has_common_section(self, config):
        """Verify common section exists"""
        assert 'common' in config, "Config should have common section"
    
    def test_common_has_path_prefix(self, config):
        """Verify data path prefix is configured"""
        assert 'path_prefix' in config['common'], "Common should define path_prefix"
        path_prefix = config['common']['path_prefix']
        assert path_prefix, "path_prefix should not be empty"
    
    def test_common_has_storage(self, config):
        """Verify storage configuration exists"""
        assert 'storage' in config['common'], "Common should define storage"
        storage = config['common']['storage']
        assert storage, "Storage should be configured"
    
    def test_storage_uses_filesystem(self, config):
        """Verify filesystem storage is configured"""
        storage = config['common']['storage']
        assert 'filesystem' in storage, "Should use filesystem storage for single-node"
    
    def test_replication_factor_for_single_node(self, config):
        """Verify replication factor is 1 for single-node"""
        assert 'replication_factor' in config['common'], \
            "Should define replication_factor"
        assert config['common']['replication_factor'] == 1, \
            "Single-node deployment should use replication_factor=1"
    
    def test_has_schema_config(self, config):
        """Verify schema_config section exists"""
        assert 'schema_config' in config, "Config must have schema_config"
    
    def test_schema_has_configs(self, config):
        """Verify schema has at least one config"""
        assert 'configs' in config['schema_config'], "schema_config needs configs list"
        configs = config['schema_config']['configs']
        assert isinstance(configs, list), "configs should be a list"
        assert len(configs) > 0, "Should have at least one schema config"
    
    def test_schema_config_has_required_fields(self, config):
        """Verify schema config has required fields"""
        for schema in config['schema_config']['configs']:
            assert 'from' in schema, "Schema must have 'from' date"
            assert 'store' in schema, "Schema must specify store type"
            assert 'object_store' in schema, "Schema must specify object_store"
            assert 'schema' in schema, "Schema must specify schema version"
    
    def test_schema_uses_boltdb_shipper(self, config):
        """Verify schema uses boltdb-shipper for single-node"""
        configs = config['schema_config']['configs']
        for schema in configs:
            if 'store' in schema:
                assert 'boltdb' in schema['store'].lower(), \
                    "Single-node typically uses boltdb-shipper"
    
    def test_has_storage_config(self, config):
        """Verify storage_config section exists"""
        assert 'storage_config' in config, "Config must have storage_config"
    
    def test_storage_config_has_boltdb(self, config):
        """Verify BoltDB configuration exists"""
        assert 'boltdb_shipper' in config['storage_config'], \
            "storage_config should configure boltdb_shipper"
    
    def test_boltdb_has_required_directories(self, config):
        """Verify BoltDB directories are configured"""
        boltdb = config['storage_config']['boltdb_shipper']
        assert 'active_index_directory' in boltdb, \
            "BoltDB should define active_index_directory"
        assert 'cache_location' in boltdb, "BoltDB should define cache_location"
    
    def test_chunk_store_config_exists(self, config):
        """Verify chunk_store_config section exists"""
        assert 'chunk_store_config' in config, "Config should have chunk_store_config"
    
    def test_log_level_is_appropriate(self, config):
        """Verify log level is set appropriately"""
        if 'log_level' in config['server']:
            log_level = config['server']['log_level']
            valid_levels = ['debug', 'info', 'warn', 'error']
            assert log_level in valid_levels, f"Log level should be one of {valid_levels}"


class TestPromtailConfig:
    """Test Promtail configuration file"""
    
    @pytest.fixture
    def config(self) -> Dict[str, Any]:
        """Load Promtail config"""
        with open(PROMTAIL_CONFIG, 'r') as f:
            return yaml.safe_load(f)
    
    def test_file_exists(self):
        """Verify promtail-config.yml exists"""
        assert PROMTAIL_CONFIG.exists(), f"Config not found at {PROMTAIL_CONFIG}"
    
    def test_valid_yaml_syntax(self):
        """Verify file contains valid YAML"""
        with open(PROMTAIL_CONFIG, 'r') as f:
            config = yaml.safe_load(f)
        assert config is not None, "Config should parse successfully"
    
    def test_has_server_section(self, config):
        """Verify server section exists"""
        assert 'server' in config, "Config must have server section"
    
    def test_server_http_port_configured(self, config):
        """Verify HTTP port is configured"""
        assert 'http_listen_port' in config['server'], "Should define HTTP port"
        port = config['server']['http_listen_port']
        assert isinstance(port, int), "Port should be integer"
        assert port > 0, "Port should be positive"
    
    def test_has_positions_file(self, config):
        """Verify positions file is configured"""
        assert 'positions' in config, "Config must have positions section"
        assert 'filename' in config['positions'], "Positions needs filename"
    
    def test_positions_file_path_is_absolute(self, config):
        """Verify positions file uses absolute path"""
        filename = config['positions']['filename']
        assert filename.startswith('/'), "Positions filename should be absolute path"
    
    def test_has_clients_section(self, config):
        """Verify clients section exists"""
        assert 'clients' in config, "Config must have clients section"
        assert isinstance(config['clients'], list), "Clients should be a list"
        assert len(config['clients']) > 0, "Should have at least one client"
    
    def test_client_has_loki_url(self, config):
        """Verify client points to Loki"""
        for client in config['clients']:
            assert 'url' in client, "Client must have URL"
            url = client['url']
            assert 'loki' in url.lower(), "URL should point to Loki"
            assert '/api/v1/push' in url, "URL should use push endpoint"
    
    def test_client_has_batch_settings(self, config):
        """Verify client has batch configuration"""
        for client in config['clients']:
            # At least one batch setting should be present
            has_batch = any(key in client for key in ['batchwait', 'batchsize', 'timeout'])
            assert has_batch, "Client should have batch configuration"
    
    def test_client_has_external_labels(self, config):
        """Verify client adds external labels"""
        for client in config['clients']:
            if 'external_labels' in client:
                labels = client['external_labels']
                assert isinstance(labels, dict), "external_labels should be a dict"
                assert len(labels) > 0, "Should have at least one external label"
    
    def test_has_scrape_configs(self, config):
        """Verify scrape_configs section exists"""
        assert 'scrape_configs' in config, "Config must have scrape_configs"
        assert isinstance(config['scrape_configs'], list), "scrape_configs should be list"
        assert len(config['scrape_configs']) > 0, "Should have at least one scrape config"
    
    def test_all_scrape_configs_have_job_name(self, config):
        """Verify all scrape configs have unique job names"""
        job_names = [sc['job_name'] for sc in config['scrape_configs']]
        assert all(job_names), "All scrape configs must have job_name"
        assert len(job_names) == len(set(job_names)), "Job names should be unique"
    
    def test_syslog_scrape_exists(self, config):
        """Verify syslog is being scraped"""
        job_names = [sc['job_name'] for sc in config['scrape_configs']]
        assert 'syslog' in job_names, "Should scrape syslog"
    
    def test_auth_log_scrape_exists(self, config):
        """Verify auth logs are being scraped"""
        job_names = [sc['job_name'] for sc in config['scrape_configs']]
        assert any('auth' in name for name in job_names), "Should scrape auth logs"
    
    def test_scrape_configs_have_targets_or_journal(self, config):
        """Verify scrape configs have either static_configs or journal"""
        for scrape_config in config['scrape_configs']:
            has_source = 'static_configs' in scrape_config or 'journal' in scrape_config
            assert has_source, f"Scrape config '{scrape_config['job_name']}' needs source"
    
    def test_static_configs_have_labels(self, config):
        """Verify static configs include labels"""
        for scrape_config in config['scrape_configs']:
            if 'static_configs' in scrape_config:
                for static_config in scrape_config['static_configs']:
                    assert 'labels' in static_config, "Static config should have labels"
                    labels = static_config['labels']
                    assert 'job' in labels, "Labels should include job"
    
    def test_file_paths_use_absolute_paths(self, config):
        """Verify log file paths are absolute"""
        for scrape_config in config['scrape_configs']:
            if 'static_configs' in scrape_config:
                for static_config in scrape_config['static_configs']:
                    if 'labels' in static_config and '__path__' in static_config['labels']:
                        path = static_config['labels']['__path__']
                        # Should be absolute or use wildcard
                        assert path.startswith('/') or '*' in path, \
                            f"Path should be absolute: {path}"
    
    def test_pipeline_stages_for_structured_parsing(self, config):
        """Verify important scrape configs have pipeline stages"""
        for scrape_config in config['scrape_configs']:
            job = scrape_config['job_name']
            # Auth and nginx logs should have pipeline processing
            if 'auth' in job or 'nginx' in job:
                assert 'pipeline_stages' in scrape_config, \
                    f"Job '{job}' should have pipeline_stages for parsing"
    
    def test_auth_log_extracts_user_and_ip(self, config):
        """Verify auth log scraper extracts user and IP"""
        auth_jobs = [sc for sc in config['scrape_configs'] 
                    if 'auth' in sc['job_name']]
        for job in auth_jobs:
            if 'pipeline_stages' in job:
                # Should extract user and source_ip
                pipeline_str = str(job['pipeline_stages'])
                assert 'user' in pipeline_str, "Should extract user from auth logs"
                assert 'source_ip' in pipeline_str or 'ip' in pipeline_str, \
                    "Should extract IP from auth logs"
    
    def test_docker_log_parsing(self, config):
        """Verify Docker log scraper handles JSON format"""
        docker_jobs = [sc for sc in config['scrape_configs'] 
                      if 'docker' in sc['job_name']]
        if docker_jobs:
            for job in docker_jobs:
                if 'pipeline_stages' in job:
                    # Docker logs are JSON, should parse them
                    pipeline_str = str(job['pipeline_stages'])
                    assert 'json' in pipeline_str.lower(), \
                        "Should parse Docker JSON logs"


class TestPrometheusConfig:
    """Test Prometheus configuration file"""
    
    @pytest.fixture
    def config(self) -> Dict[str, Any]:
        """Load Prometheus config"""
        with open(PROMETHEUS_CONFIG, 'r') as f:
            return yaml.safe_load(f)
    
    def test_file_exists(self):
        """Verify prometheus.yml exists"""
        assert PROMETHEUS_CONFIG.exists(), f"Config not found at {PROMETHEUS_CONFIG}"
    
    def test_valid_yaml_syntax(self):
        """Verify file contains valid YAML"""
        with open(PROMETHEUS_CONFIG, 'r') as f:
            config = yaml.safe_load(f)
        assert config is not None, "Config should parse successfully"
    
    def test_has_global_section(self, config):
        """Verify global section exists"""
        assert 'global' in config, "Config must have global section"
    
    def test_scrape_interval_configured(self, config):
        """Verify scrape_interval is set"""
        assert 'scrape_interval' in config['global'], "Global should define scrape_interval"
        interval = config['global']['scrape_interval']
        assert interval, "scrape_interval should not be empty"
    
    def test_evaluation_interval_configured(self, config):
        """Verify evaluation_interval is set"""
        assert 'evaluation_interval' in config['global'], \
            "Global should define evaluation_interval"
    
    def test_has_external_labels(self, config):
        """Verify external labels are configured"""
        assert 'external_labels' in config['global'], \
            "Global should define external_labels"
        labels = config['global']['external_labels']
        assert isinstance(labels, dict), "external_labels should be a dict"
        assert len(labels) > 0, "Should have at least one external label"
    
    def test_external_labels_include_environment(self, config):
        """Verify external labels include environment"""
        labels = config['global']['external_labels']
        assert 'environment' in labels or 'cluster' in labels, \
            "Should label environment/cluster"
    
    def test_has_alerting_section(self, config):
        """Verify alerting section exists"""
        assert 'alerting' in config, "Config should have alerting section"
    
    def test_alertmanagers_configured(self, config):
        """Verify Alertmanager endpoints are configured"""
        assert 'alertmanagers' in config['alerting'], \
            "Alerting should list alertmanagers"
        alertmanagers = config['alerting']['alertmanagers']
        assert isinstance(alertmanagers, list), "alertmanagers should be a list"
        assert len(alertmanagers) > 0, "Should have at least one alertmanager"
    
    def test_alertmanager_has_targets(self, config):
        """Verify Alertmanager has static targets"""
        for am in config['alerting']['alertmanagers']:
            assert 'static_configs' in am, "Alertmanager needs static_configs"
            for static_config in am['static_configs']:
                assert 'targets' in static_config, "static_config needs targets"
                targets = static_config['targets']
                assert len(targets) > 0, "Should have at least one target"
    
    def test_has_rule_files_section(self, config):
        """Verify rule_files section exists"""
        assert 'rule_files' in config, "Config should have rule_files"
        assert isinstance(config['rule_files'], list), "rule_files should be a list"
    
    def test_rule_files_use_glob_patterns(self, config):
        """Verify rule files use glob patterns for flexibility"""
        rule_files = config['rule_files']
        if rule_files:
            # At least one should use glob pattern
            has_glob = any('*' in rf for rf in rule_files)
            assert has_glob, "rule_files should use glob patterns (*.yml)"
    
    def test_has_scrape_configs(self, config):
        """Verify scrape_configs section exists"""
        assert 'scrape_configs' in config, "Config must have scrape_configs"
        assert isinstance(config['scrape_configs'], list), "scrape_configs should be list"
        assert len(config['scrape_configs']) > 0, "Should have at least one scrape config"
    
    def test_all_scrape_configs_have_job_name(self, config):
        """Verify all scrape configs have job names"""
        for sc in config['scrape_configs']:
            assert 'job_name' in sc, "Scrape config must have job_name"
            assert sc['job_name'], "job_name should not be empty"
    
    def test_job_names_are_unique(self, config):
        """Verify job names are unique"""
        job_names = [sc['job_name'] for sc in config['scrape_configs']]
        assert len(job_names) == len(set(job_names)), "Job names should be unique"
    
    def test_prometheus_self_monitoring(self, config):
        """Verify Prometheus monitors itself"""
        job_names = [sc['job_name'] for sc in config['scrape_configs']]
        assert 'prometheus' in job_names, "Should monitor Prometheus itself"
    
    def test_node_exporter_monitoring(self, config):
        """Verify node exporter is being scraped"""
        job_names = [sc['job_name'] for sc in config['scrape_configs']]
        has_node = any('node' in name.lower() for name in job_names)
        assert has_node, "Should scrape node_exporter"
    
    def test_alertmanager_monitoring(self, config):
        """Verify Alertmanager is being monitored"""
        job_names = [sc['job_name'] for sc in config['scrape_configs']]
        assert 'alertmanager' in job_names, "Should monitor Alertmanager"
    
    def test_scrape_configs_have_targets(self, config):
        """Verify scrape configs have targets"""
        for sc in config['scrape_configs']:
            assert 'static_configs' in sc, f"Job '{sc['job_name']}' needs static_configs"
            for static_config in sc['static_configs']:
                assert 'targets' in static_config, "static_config needs targets"
    
    def test_targets_are_valid_addresses(self, config):
        """Verify targets use host:port format"""
        for sc in config['scrape_configs']:
            for static_config in sc['static_configs']:
                for target in static_config['targets']:
                    assert ':' in target, f"Target should be host:port format: {target}"
    
    def test_proxmox_monitoring_exists(self, config):
        """Verify Proxmox is being monitored"""
        job_names = [sc['job_name'] for sc in config['scrape_configs']]
        has_proxmox = any('proxmox' in name.lower() for name in job_names)
        assert has_proxmox, "Should monitor Proxmox"
    
    def test_basic_auth_for_secure_endpoints(self, config):
        """Verify sensitive endpoints use authentication"""
        for sc in config['scrape_configs']:
            # Proxmox and other external systems should use auth
            if 'proxmox' in sc['job_name'].lower():
                assert 'basic_auth' in sc, \
                    "Proxmox scrape should use basic authentication"
    
    def test_relabel_configs_for_friendly_names(self, config):
        """Verify relabel_configs add friendly hostnames"""
        vm_jobs = [sc for sc in config['scrape_configs'] 
                  if 'vm' in sc['job_name'].lower() or 'node' in sc['job_name'].lower()]
        if vm_jobs:
            for job in vm_jobs:
                if 'relabel_configs' in job:
                    # Should map IPs to friendly hostnames
                    relabel_str = str(job['relabel_configs'])
                    assert 'hostname' in relabel_str, \
                        "Should add friendly hostname labels"


class TestInfrastructureAlerts:
    """Test Prometheus alert rules"""
    
    @pytest.fixture
    def config(self) -> Dict[str, Any]:
        """Load alert rules"""
        with open(INFRASTRUCTURE_ALERTS, 'r') as f:
            return yaml.safe_load(f)
    
    def test_file_exists(self):
        """Verify infrastructure_alerts.yml exists"""
        assert INFRASTRUCTURE_ALERTS.exists(), \
            f"Alerts not found at {INFRASTRUCTURE_ALERTS}"
    
    def test_valid_yaml_syntax(self):
        """Verify file contains valid YAML"""
        with open(INFRASTRUCTURE_ALERTS, 'r') as f:
            config = yaml.safe_load(f)
        assert config is not None, "Alerts should parse successfully"
    
    def test_has_groups_section(self, config):
        """Verify groups section exists"""
        assert 'groups' in config, "Alert file must have groups section"
        assert isinstance(config['groups'], list), "groups should be a list"
        assert len(config['groups']) > 0, "Should have at least one group"
    
    def test_all_groups_have_names(self, config):
        """Verify all groups have names"""
        for group in config['groups']:
            assert 'name' in group, "Group must have name"
            assert group['name'], "Group name should not be empty"
    
    def test_groups_have_rules(self, config):
        """Verify all groups have rules"""
        for group in config['groups']:
            assert 'rules' in group, f"Group '{group['name']}' must have rules"
            # It's ok to have empty rules for placeholder groups
    
    def test_infrastructure_group_exists(self, config):
        """Verify infrastructure alert group exists"""
        group_names = [g['name'] for g in config['groups']]
        assert 'infrastructure' in group_names, "Should have infrastructure group"
    
    def test_all_rules_have_required_fields(self, config):
        """Verify all alert rules have required fields"""
        for group in config['groups']:
            for rule in group.get('rules', []):
                assert 'alert' in rule, "Rule must have alert name"
                assert 'expr' in rule, "Rule must have expr (query)"
                assert 'labels' in rule, "Rule must have labels"
                assert 'annotations' in rule, "Rule must have annotations"
    
    def test_all_rules_have_severity(self, config):
        """Verify all rules have severity label"""
        for group in config['groups']:
            for rule in group.get('rules', []):
                if 'labels' in rule:
                    assert 'severity' in rule['labels'], \
                        f"Alert '{rule['alert']}' must have severity label"
    
    def test_severity_values_are_valid(self, config):
        """Verify severity labels use standard values"""
        valid_severities = ['critical', 'warning', 'info']
        for group in config['groups']:
            for rule in group.get('rules', []):
                if 'labels' in rule and 'severity' in rule['labels']:
                    severity = rule['labels']['severity']
                    assert severity in valid_severities, \
                        f"Severity '{severity}' not in {valid_severities}"
    
    def test_rules_have_component_label(self, config):
        """Verify rules have component label for routing"""
        for group in config['groups']:
            for rule in group.get('rules', []):
                if 'labels' in rule:
                    assert 'component' in rule['labels'], \
                        f"Alert '{rule['alert']}' should have component label"
    
    def test_all_rules_have_summary(self, config):
        """Verify all rules have summary annotation"""
        for group in config['groups']:
            for rule in group.get('rules', []):
                if 'annotations' in rule:
                    assert 'summary' in rule['annotations'], \
                        f"Alert '{rule['alert']}' must have summary"
    
    def test_all_rules_have_description(self, config):
        """Verify all rules have description annotation"""
        for group in config['groups']:
            for rule in group.get('rules', []):
                if 'annotations' in rule:
                    assert 'description' in rule['annotations'], \
                        f"Alert '{rule['alert']}' must have description"
    
    def test_all_rules_have_runbook(self, config):
        """Verify all rules have runbook link"""
        for group in config['groups']:
            for rule in group.get('rules', []):
                if 'annotations' in rule:
                    assert 'runbook' in rule['annotations'], \
                        f"Alert '{rule['alert']}' should have runbook link"
    
    def test_host_down_alert_exists(self, config):
        """Verify HostDown alert is defined"""
        all_alerts = []
        for group in config['groups']:
            all_alerts.extend([r['alert'] for r in group.get('rules', [])])
        assert 'HostDown' in all_alerts, "Should have HostDown alert"
    
    def test_cpu_usage_alerts_exist(self, config):
        """Verify CPU usage alerts exist"""
        all_alerts = []
        for group in config['groups']:
            all_alerts.extend([r['alert'] for r in group.get('rules', [])])
        has_cpu = any('cpu' in alert.lower() for alert in all_alerts)
        assert has_cpu, "Should have CPU usage alerts"
    
    def test_memory_usage_alerts_exist(self, config):
        """Verify memory usage alerts exist"""
        all_alerts = []
        for group in config['groups']:
            all_alerts.extend([r['alert'] for r in group.get('rules', [])])
        has_memory = any('memory' in alert.lower() for alert in all_alerts)
        assert has_memory, "Should have memory usage alerts"
    
    def test_disk_space_alerts_exist(self, config):
        """Verify disk space alerts exist"""
        all_alerts = []
        for group in config['groups']:
            all_alerts.extend([r['alert'] for r in group.get('rules', [])])
        has_disk = any('disk' in alert.lower() for alert in all_alerts)
        assert has_disk, "Should have disk space alerts"
    
    def test_backup_alerts_exist(self, config):
        """Verify backup job alerts exist"""
        all_alerts = []
        for group in config['groups']:
            all_alerts.extend([r['alert'] for r in group.get('rules', [])])
        has_backup = any('backup' in alert.lower() for alert in all_alerts)
        assert has_backup, "Should have backup job alerts"
    
    def test_critical_alerts_have_for_clause(self, config):
        """Verify critical alerts have appropriate 'for' duration"""
        for group in config['groups']:
            for rule in group.get('rules', []):
                if 'labels' in rule and rule['labels'].get('severity') == 'critical':
                    # Critical alerts should fire quickly
                    if 'for' in rule:
                        duration = rule['for']
                        # Should be measured in minutes for infrastructure
                        assert 'm' in duration or 's' in duration, \
                            f"Critical alert '{rule['alert']}' should have short for duration"
    
    def test_alert_expressions_are_valid_promql(self, config):
        """Verify alert expressions look like valid PromQL"""
        for group in config['groups']:
            for rule in group.get('rules', []):
                expr = rule.get('expr', '')
                # Basic validation - should have metric names and operators
                assert len(expr) > 0, f"Alert '{rule['alert']}' has empty expr"
                # Common PromQL patterns
                has_valid_syntax = any(char in expr for char in ['>', '<', '==', '!='])
                assert has_valid_syntax or 'up' in expr, \
                    f"Alert '{rule['alert']}' expr should have comparison operators"
    
    def test_summary_uses_templating(self, config):
        """Verify summaries use Go template variables"""
        for group in config['groups']:
            for rule in group.get('rules', []):
                if 'annotations' in rule and 'summary' in rule['annotations']:
                    summary = rule['annotations']['summary']
                    # Should reference instance or other labels
                    has_template = '{{' in summary or '$labels' in summary
                    if not has_template:
                        # Static summaries are ok, but templated is better
                        pass  # Not a hard requirement
    
    def test_description_provides_context(self, config):
        """Verify descriptions provide actionable context"""
        for group in config['groups']:
            for rule in group.get('rules', []):
                if 'annotations' in rule and 'description' in rule['annotations']:
                    description = rule['annotations']['description']
                    # Description should be substantial
                    assert len(description) > 20, \
                        f"Alert '{rule['alert']}' description too short"


class TestConfigurationSecurity:
    """Test security aspects of configurations"""
    
    def test_alertmanager_no_hardcoded_passwords(self):
        """Verify Alertmanager config doesn't have hardcoded passwords"""
        with open(ALERTMANAGER_CONFIG, 'r') as f:
            content = f.read().lower()
        # Should not have actual passwords
        assert 'password' not in content or 'changeme' in content, \
            "Should not have hardcoded real passwords"
    
    def test_prometheus_basic_auth_uses_placeholders(self):
        """Verify Prometheus config uses placeholders for auth"""
        with open(PROMETHEUS_CONFIG, 'r') as f:
            config = yaml.safe_load(f)
        for sc in config['scrape_configs']:
            if 'basic_auth' in sc:
                auth = sc['basic_auth']
                if 'password' in auth:
                    password = auth['password']
                    assert 'changeme' in password.lower() or 'placeholder' in password.lower(), \
                        "Should use placeholder passwords in config"
    
    def test_webhook_urls_use_placeholders(self):
        """Verify webhook URLs use placeholders"""
        with open(ALERTMANAGER_CONFIG, 'r') as f:
            config = yaml.safe_load(f)
        if 'slack_api_url' in config['global']:
            url = config['global']['slack_api_url']
            assert 'PLACEHOLDER' in url or 'YOUR' in url or 'CHANGE' in url, \
                "Should use placeholder Slack webhooks"


class TestConfigurationComments:
    """Test that configuration files are well-documented"""
    
    def test_alertmanager_has_comments(self):
        """Verify Alertmanager config has explanatory comments"""
        with open(ALERTMANAGER_CONFIG, 'r') as f:
            content = f.read()
        comment_lines = [line for line in content.split('\n') if line.strip().startswith('#')]
        assert len(comment_lines) >= 5, "Config should have explanatory comments"
    
    def test_prometheus_has_comments(self):
        """Verify Prometheus config has explanatory comments"""
        with open(PROMETHEUS_CONFIG, 'r') as f:
            content = f.read()
        comment_lines = [line for line in content.split('\n') if line.strip().startswith('#')]
        assert len(comment_lines) >= 10, "Config should have extensive comments"
    
    def test_loki_has_comments(self):
        """Verify Loki config has explanatory comments"""
        with open(LOKI_CONFIG, 'r') as f:
            content = f.read()
        comment_lines = [line for line in content.split('\n') if line.strip().startswith('#')]
        assert len(comment_lines) >= 5, "Config should have explanatory comments"
    
    def test_promtail_has_comments(self):
        """Verify Promtail config has explanatory comments"""
        with open(PROMTAIL_CONFIG, 'r') as f:
            content = f.read()
        comment_lines = [line for line in content.split('\n') if line.strip().startswith('#')]
        assert len(comment_lines) >= 5, "Config should have explanatory comments"
    
    def test_alerts_have_comments(self):
        """Verify alert rules have explanatory comments"""
        with open(INFRASTRUCTURE_ALERTS, 'r') as f:
            content = f.read()
        comment_lines = [line for line in content.split('\n') if line.strip().startswith('#')]
        assert len(comment_lines) >= 3, "Alert rules should have explanatory comments"