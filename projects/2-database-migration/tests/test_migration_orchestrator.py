"""
Tests for Database Migration Orchestrator
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timezone

# Import the module under test
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from migration_orchestrator import (
    DatabaseMigrationOrchestrator,
    DatabaseConfig,
    MigrationPhase,
    MigrationMetrics
)


class TestDatabaseConfig:
    """Test DatabaseConfig dataclass"""

    def test_database_config_creation(self):
        """Test creating a database configuration"""
        config = DatabaseConfig(
            host="localhost",
            port=5432,
            database="testdb",
            username="testuser",
            password="testpass"
        )

        assert config.host == "localhost"
        assert config.port == 5432
        assert config.database == "testdb"
        assert config.username == "testuser"
        assert config.password == "testpass"
        assert config.ssl_mode == "require"  # Default value

    def test_database_config_with_custom_ssl(self):
        """Test database config with custom SSL mode"""
        config = DatabaseConfig(
            host="localhost",
            port=5432,
            database="testdb",
            username="testuser",
            password="testpass",
            ssl_mode="disable"
        )

        assert config.ssl_mode == "disable"


class TestMigrationMetrics:
    """Test MigrationMetrics dataclass"""

    def test_metrics_creation(self):
        """Test creating migration metrics"""
        start_time = datetime.now(timezone.utc)
        metrics = MigrationMetrics(
            replication_lag_seconds=2.5,
            rows_migrated=1000,
            errors_count=0,
            start_time=start_time
        )

        assert metrics.replication_lag_seconds == 2.5
        assert metrics.rows_migrated == 1000
        assert metrics.errors_count == 0
        assert metrics.start_time == start_time
        assert metrics.end_time is None
        assert metrics.downtime_seconds == 0.0

    def test_metrics_duration_calculation(self):
        """Test duration calculation"""
        start_time = datetime(2025, 1, 1, 10, 0, 0)
        end_time = datetime(2025, 1, 1, 10, 30, 0)

        metrics = MigrationMetrics(
            replication_lag_seconds=0.0,
            rows_migrated=1000,
            errors_count=0,
            start_time=start_time,
            end_time=end_time
        )

        duration = metrics.get_duration()
        assert duration.total_seconds() == 1800  # 30 minutes


class TestDatabaseMigrationOrchestrator:
    """Test DatabaseMigrationOrchestrator class"""

    @pytest.fixture
    def source_config(self):
        """Source database configuration fixture"""
        return DatabaseConfig(
            host="source.example.com",
            port=5432,
            database="source_db",
            username="source_user",
            password="source_pass"
        )

    @pytest.fixture
    def target_config(self):
        """Target database configuration fixture"""
        return DatabaseConfig(
            host="target.example.com",
            port=5432,
            database="target_db",
            username="target_user",
            password="target_pass"
        )

    @pytest.fixture
    def orchestrator(self, source_config, target_config):
        """Migration orchestrator fixture"""
        with patch('migration_orchestrator.boto3'):
            return DatabaseMigrationOrchestrator(
                source_config=source_config,
                target_config=target_config,
                max_replication_lag_seconds=5
            )

    def test_orchestrator_initialization(self, orchestrator, source_config, target_config):
        """Test orchestrator initialization"""
        assert orchestrator.source_config == source_config
        assert orchestrator.target_config == target_config
        assert orchestrator.max_lag == 5
        assert orchestrator.validation_sample_size == 1000
        assert orchestrator.phase == MigrationPhase.INIT
        assert isinstance(orchestrator.metrics, MigrationMetrics)

    @patch('migration_orchestrator.psycopg2.connect')
    def test_validate_connectivity_success(self, mock_connect, orchestrator):
        """Test successful connectivity validation"""
        # Mock database connections
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ['PostgreSQL 15.4']

        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        result = orchestrator.validate_connectivity()

        assert result is True
        assert mock_connect.call_count == 2  # Source and target

    @patch('migration_orchestrator.psycopg2.connect')
    def test_validate_connectivity_failure(self, mock_connect, orchestrator):
        """Test connectivity validation failure"""
        # Simulate connection error
        mock_connect.side_effect = Exception("Connection failed")

        result = orchestrator.validate_connectivity()

        assert result is False

    def test_setup_replication_without_dms(self, orchestrator):
        """Test replication setup without DMS"""
        with patch.object(orchestrator, '_setup_debezium_replication') as mock_debezium:
            result = orchestrator.setup_replication()

            assert result is True
            assert orchestrator.phase == MigrationPhase.REPLICATION
            mock_debezium.assert_called_once()

    @patch('migration_orchestrator.boto3.client')
    def test_setup_replication_with_dms(self, mock_boto_client, source_config, target_config):
        """Test replication setup with DMS"""
        mock_dms_client = MagicMock()
        mock_dms_client.create_replication_task.return_value = {
            'ReplicationTask': {
                'ReplicationTaskArn': 'arn:aws:dms:us-west-2:123456789012:task:test'
            }
        }
        mock_boto_client.return_value = mock_dms_client

        orchestrator = DatabaseMigrationOrchestrator(
            source_config=source_config,
            target_config=target_config,
            dms_replication_instance_arn='arn:aws:dms:us-west-2:123456789012:rep:test'
        )

        with patch.object(orchestrator, '_create_dms_endpoint', return_value='endpoint-arn'):
            result = orchestrator.setup_replication()

            assert result is True
            mock_dms_client.create_replication_task.assert_called_once()
            mock_dms_client.start_replication_task.assert_called_once()

    def test_measure_replication_lag(self, orchestrator):
        """Test replication lag measurement"""
        with patch.object(orchestrator, '_get_connection') as mock_get_conn:
            # Mock database connections
            mock_source_conn = MagicMock()
            mock_target_conn = MagicMock()

            mock_source_cursor = MagicMock()
            mock_source_cursor.fetchone.return_value = [1609459200.0]  # 2021-01-01 00:00:00

            mock_target_cursor = MagicMock()
            mock_target_cursor.fetchone.return_value = [1609459195.0]  # 5 seconds behind

            mock_source_conn.cursor.return_value.__enter__.return_value = mock_source_cursor
            mock_target_conn.cursor.return_value.__enter__.return_value = mock_target_cursor

            mock_get_conn.side_effect = [mock_source_conn, mock_target_conn]

            lag = orchestrator._measure_replication_lag()

            assert lag == 5.0

    @patch.object(DatabaseMigrationOrchestrator, '_measure_replication_lag', return_value=2.0)
    @patch.object(DatabaseMigrationOrchestrator, '_validate_data_consistency', return_value=True)
    @patch.object(DatabaseMigrationOrchestrator, '_validate_row_counts', return_value=True)
    def test_validate_replication_success(
        self,
        mock_row_counts,
        mock_data_consistency,
        mock_lag,
        orchestrator
    ):
        """Test successful replication validation"""
        result = orchestrator.validate_replication()

        assert result is True
        assert orchestrator.phase == MigrationPhase.VALIDATION
        assert orchestrator.metrics.replication_lag_seconds == 2.0

    @patch.object(DatabaseMigrationOrchestrator, '_measure_replication_lag', return_value=10.0)
    def test_validate_replication_lag_too_high(self, mock_lag, orchestrator):
        """Test replication validation fails when lag is too high"""
        result = orchestrator.validate_replication()

        assert result is False

    @patch.object(DatabaseMigrationOrchestrator, 'validate_replication', return_value=True)
    @patch.object(DatabaseMigrationOrchestrator, '_pause_application_writes')
    @patch.object(DatabaseMigrationOrchestrator, '_wait_for_replication_sync')
    @patch.object(DatabaseMigrationOrchestrator, '_switch_application_traffic')
    @patch.object(DatabaseMigrationOrchestrator, '_verify_target_operations', return_value=True)
    def test_perform_cutover_success(
        self,
        mock_verify,
        mock_switch,
        mock_wait,
        mock_pause,
        mock_validate,
        orchestrator
    ):
        """Test successful cutover"""
        result = orchestrator.perform_cutover()

        assert result is True
        assert orchestrator.phase == MigrationPhase.COMPLETE
        assert orchestrator.metrics.end_time is not None
        assert orchestrator.metrics.downtime_seconds > 0

    @patch.object(DatabaseMigrationOrchestrator, '_pause_application_writes')
    @patch.object(DatabaseMigrationOrchestrator, '_wait_for_replication_sync')
    @patch.object(DatabaseMigrationOrchestrator, 'validate_replication', side_effect=Exception("Validation failed"))
    @patch.object(DatabaseMigrationOrchestrator, 'rollback', return_value=True)
    def test_perform_cutover_failure_triggers_rollback(
        self,
        mock_rollback,
        mock_validate,
        mock_wait,
        mock_pause,
        orchestrator
    ):
        """Test cutover failure triggers rollback"""
        result = orchestrator.perform_cutover()

        assert result is False
        assert orchestrator.metrics.errors_count > 0
        mock_rollback.assert_called_once()

    def test_rollback(self, orchestrator):
        """Test rollback procedure"""
        with patch.object(orchestrator, '_switch_to_source'):
            with patch.object(orchestrator, '_stop_replication'):
                with patch.object(orchestrator, 'validate_connectivity', return_value=True):
                    result = orchestrator.rollback()

                    assert result is True
                    assert orchestrator.phase == MigrationPhase.ROLLBACK

    @patch.object(DatabaseMigrationOrchestrator, 'validate_connectivity', return_value=True)
    @patch.object(DatabaseMigrationOrchestrator, 'setup_replication', return_value=True)
    @patch.object(DatabaseMigrationOrchestrator, 'validate_replication', return_value=True)
    @patch.object(DatabaseMigrationOrchestrator, 'perform_cutover', return_value=True)
    @patch.object(DatabaseMigrationOrchestrator, 'publish_metrics')
    def test_run_migration_success(
        self,
        mock_publish,
        mock_cutover,
        mock_validate,
        mock_setup,
        mock_connectivity,
        orchestrator
    ):
        """Test complete migration workflow success"""
        result = orchestrator.run_migration()

        assert result is True
        mock_connectivity.assert_called_once()
        mock_setup.assert_called_once()
        mock_validate.assert_called()
        mock_cutover.assert_called_once()
        mock_publish.assert_called_once()

    @patch.object(DatabaseMigrationOrchestrator, 'validate_connectivity', return_value=False)
    def test_run_migration_fails_on_connectivity(self, mock_connectivity, orchestrator):
        """Test migration fails on connectivity check"""
        result = orchestrator.run_migration()

        assert result is False
        assert orchestrator.phase == MigrationPhase.FAILED

    def test_table_mappings_json_format(self, orchestrator):
        """Test table mappings are valid JSON"""
        import json
        mappings = orchestrator._get_table_mappings()
        parsed = json.loads(mappings)

        assert 'rules' in parsed
        assert len(parsed['rules']) > 0

    def test_replication_settings_json_format(self, orchestrator):
        """Test replication settings are valid JSON"""
        import json
        settings = orchestrator._get_replication_settings()
        parsed = json.loads(settings)

        assert 'TargetMetadata' in parsed
        assert 'FullLoadSettings' in parsed
        assert 'Logging' in parsed


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
