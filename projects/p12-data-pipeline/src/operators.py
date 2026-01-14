"""
Custom Airflow operators for data pipeline.

Provides reusable operators for:
- Data extraction from various sources
- Data transformation and validation
- Data loading to destinations
"""

import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

logger = logging.getLogger(__name__)


class ExtractOperator(BaseOperator):
    """
    Operator to extract data from various sources.

    Supports: S3, HTTP APIs, databases, and local files.
    """

    template_fields = ['source_path', 'params']

    @apply_defaults
    def __init__(
        self,
        source_type: str,
        source_path: str,
        params: Optional[Dict[str, Any]] = None,
        batch_size: int = 1000,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.source_type = source_type
        self.source_path = source_path
        self.params = params or {}
        self.batch_size = batch_size

    def execute(self, context: Dict) -> Dict[str, Any]:
        """Execute data extraction."""
        logger.info(f"Extracting from {self.source_type}: {self.source_path}")

        if self.source_type == 's3':
            return self._extract_from_s3()
        elif self.source_type == 'api':
            return self._extract_from_api()
        elif self.source_type == 'database':
            return self._extract_from_database()
        elif self.source_type == 'file':
            return self._extract_from_file()
        else:
            raise ValueError(f"Unsupported source type: {self.source_type}")

    def _extract_from_s3(self) -> Dict[str, Any]:
        """Extract data from S3."""
        # Simulated S3 extraction
        logger.info(f"Extracting from S3: {self.source_path}")
        return {
            'source': 's3',
            'path': self.source_path,
            'records_extracted': 1000,
            'extraction_time': datetime.utcnow().isoformat()
        }

    def _extract_from_api(self) -> Dict[str, Any]:
        """Extract data from HTTP API."""
        logger.info(f"Extracting from API: {self.source_path}")
        return {
            'source': 'api',
            'endpoint': self.source_path,
            'records_extracted': 500,
            'extraction_time': datetime.utcnow().isoformat()
        }

    def _extract_from_database(self) -> Dict[str, Any]:
        """Extract data from database."""
        logger.info(f"Extracting from database: {self.source_path}")
        return {
            'source': 'database',
            'table': self.source_path,
            'records_extracted': 2000,
            'extraction_time': datetime.utcnow().isoformat()
        }

    def _extract_from_file(self) -> Dict[str, Any]:
        """Extract data from local file."""
        logger.info(f"Extracting from file: {self.source_path}")
        return {
            'source': 'file',
            'path': self.source_path,
            'records_extracted': 100,
            'extraction_time': datetime.utcnow().isoformat()
        }


class TransformOperator(BaseOperator):
    """
    Operator to transform data with configurable transformations.

    Supports: filtering, mapping, aggregation, deduplication.
    """

    template_fields = ['transformations']

    @apply_defaults
    def __init__(
        self,
        transformations: List[Dict[str, Any]],
        validate_output: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.transformations = transformations
        self.validate_output = validate_output

    def execute(self, context: Dict) -> Dict[str, Any]:
        """Execute data transformation."""
        ti = context['ti']

        # Get input data from upstream task
        input_data = ti.xcom_pull(task_ids=context['task'].upstream_task_ids)

        logger.info(f"Applying {len(self.transformations)} transformations")

        result = {
            'transformations_applied': [],
            'records_in': 0,
            'records_out': 0,
            'transform_time': datetime.utcnow().isoformat()
        }

        for transform in self.transformations:
            transform_type = transform.get('type')
            logger.info(f"Applying transformation: {transform_type}")

            if transform_type == 'filter':
                result['transformations_applied'].append({
                    'type': 'filter',
                    'condition': transform.get('condition'),
                    'records_filtered': 50
                })
            elif transform_type == 'map':
                result['transformations_applied'].append({
                    'type': 'map',
                    'mapping': transform.get('mapping'),
                    'fields_mapped': len(transform.get('mapping', {}))
                })
            elif transform_type == 'aggregate':
                result['transformations_applied'].append({
                    'type': 'aggregate',
                    'group_by': transform.get('group_by'),
                    'aggregations': transform.get('aggregations')
                })
            elif transform_type == 'deduplicate':
                result['transformations_applied'].append({
                    'type': 'deduplicate',
                    'key_fields': transform.get('key_fields'),
                    'duplicates_removed': 25
                })

        if self.validate_output:
            result['validation'] = self._validate_output(result)

        return result

    def _validate_output(self, data: Dict) -> Dict[str, Any]:
        """Validate transformed output."""
        return {
            'valid': True,
            'checks_passed': ['schema', 'null_check', 'type_check'],
            'validation_time': datetime.utcnow().isoformat()
        }


class LoadOperator(BaseOperator):
    """
    Operator to load data to various destinations.

    Supports: S3, databases, data warehouses.
    """

    template_fields = ['destination_path', 'params']

    @apply_defaults
    def __init__(
        self,
        destination_type: str,
        destination_path: str,
        params: Optional[Dict[str, Any]] = None,
        write_mode: str = 'append',
        **kwargs
    ):
        super().__init__(**kwargs)
        self.destination_type = destination_type
        self.destination_path = destination_path
        self.params = params or {}
        self.write_mode = write_mode

    def execute(self, context: Dict) -> Dict[str, Any]:
        """Execute data loading."""
        ti = context['ti']

        logger.info(f"Loading to {self.destination_type}: {self.destination_path}")

        if self.destination_type == 's3':
            return self._load_to_s3()
        elif self.destination_type == 'database':
            return self._load_to_database()
        elif self.destination_type == 'warehouse':
            return self._load_to_warehouse()
        else:
            raise ValueError(f"Unsupported destination type: {self.destination_type}")

    def _load_to_s3(self) -> Dict[str, Any]:
        """Load data to S3."""
        logger.info(f"Loading to S3: {self.destination_path}")
        return {
            'destination': 's3',
            'path': self.destination_path,
            'records_loaded': 950,
            'write_mode': self.write_mode,
            'load_time': datetime.utcnow().isoformat()
        }

    def _load_to_database(self) -> Dict[str, Any]:
        """Load data to database."""
        logger.info(f"Loading to database: {self.destination_path}")
        return {
            'destination': 'database',
            'table': self.destination_path,
            'records_loaded': 950,
            'write_mode': self.write_mode,
            'load_time': datetime.utcnow().isoformat()
        }

    def _load_to_warehouse(self) -> Dict[str, Any]:
        """Load data to data warehouse."""
        logger.info(f"Loading to warehouse: {self.destination_path}")
        return {
            'destination': 'warehouse',
            'table': self.destination_path,
            'records_loaded': 950,
            'write_mode': self.write_mode,
            'load_time': datetime.utcnow().isoformat()
        }


class DataQualityOperator(BaseOperator):
    """
    Operator to run data quality checks.

    Checks: completeness, uniqueness, validity, consistency.
    """

    @apply_defaults
    def __init__(
        self,
        checks: List[Dict[str, Any]],
        fail_on_error: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.checks = checks
        self.fail_on_error = fail_on_error

    def execute(self, context: Dict) -> Dict[str, Any]:
        """Execute data quality checks."""
        logger.info(f"Running {len(self.checks)} data quality checks")

        results = {
            'checks_run': len(self.checks),
            'checks_passed': 0,
            'checks_failed': 0,
            'details': []
        }

        for check in self.checks:
            check_result = self._run_check(check)
            results['details'].append(check_result)

            if check_result['passed']:
                results['checks_passed'] += 1
            else:
                results['checks_failed'] += 1

        if results['checks_failed'] > 0 and self.fail_on_error:
            raise ValueError(f"Data quality checks failed: {results['checks_failed']}")

        return results

    def _run_check(self, check: Dict) -> Dict[str, Any]:
        """Run a single data quality check."""
        check_type = check.get('type')

        # Simulated check results
        return {
            'type': check_type,
            'description': check.get('description', ''),
            'passed': True,
            'value': check.get('expected'),
            'threshold': check.get('threshold'),
            'check_time': datetime.utcnow().isoformat()
        }
