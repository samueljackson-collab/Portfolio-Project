# P12 Data Pipeline (Airflow) - Setup Guide

## Overview

This project contains a complete Airflow ETL data pipeline with Docker Compose setup for local development and testing. The pipeline includes:

- **Extract DAG**: Extracts data from source databases
- **Transform DAG**: Cleans and transforms data with quality checks
- **Load DAG**: Loads transformed data into data warehouse
- **Analytics DAG**: Generates daily analytics reports

## Prerequisites

Before you begin, ensure you have installed:

- Docker (version 20.10+)
- Docker Compose (version 1.29+)
- Python 3.9+ (for local testing)
- Git

## Quick Start

### 1. Clone/Navigate to the Project

```bash
cd /workspace/Portfolio-Project/projects-new/P12-data-pipeline-airflow
```

### 2. Start Airflow Services

```bash
# Start all services in the background
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 3. Access Airflow UI

Once services are running, access the Airflow web interface:

- **Airflow Web UI**: http://localhost:8080
- **Default credentials**:
  - Username: `airflow`
  - Password: `airflow`

### 4. Monitor Celery Tasks

View Celery task queue and worker status:

- **Flower UI**: http://localhost:5555

## Architecture

### Services

The `docker-compose.yml` includes:

1. **PostgreSQL** (`postgres:13-alpine`)
   - Metadata database for Airflow
   - Port: `5432`
   - Credentials: `airflow/airflow`

2. **Redis** (`redis:7-alpine`)
   - Message broker for Celery
   - Port: `6379`

3. **Airflow Webserver** (`apache/airflow:2.7.3`)
   - Web UI for DAG management
   - Port: `8080`
   - Executor: CeleryExecutor

4. **Airflow Scheduler** (`apache/airflow:2.7.3`)
   - Parses DAGs and schedules tasks
   - Communicates via Redis broker

5. **Celery Workers** (2 instances)
   - Execute tasks from the queue
   - Scalable (add more by duplicating config)

6. **Flower** (Celery monitoring)
   - Monitor worker status and tasks
   - Port: `5555`

### DAGs

#### ETL Extract Data (`etl_extract_data.py`)

**Schedule**: Daily at 01:00 UTC

**Tasks**:
- `extract_from_source`: Connects to source database and extracts data
- `validate_extracted_data`: Validates row counts and schema
- `notify_extraction_complete`: Sends completion notification

**Pattern**: Linear dependency chain

#### ETL Transform Data (`etl_transform_data.py`)

**Schedule**: Daily at 02:00 UTC

**Tasks**:
- `clean_data`: Remove duplicates, handle nulls, standardize formats
- `apply_transformations`: Apply business logic and calculations
- `check_data_quality`: Validate data quality metrics
- `decide_quality_branch`: Branch based on quality score
- `quality_alert`: Alert if quality threshold not met
- `notify_transform_complete`: Notify on success

**Pattern**: Branching workflow with quality gates

#### ETL Load Warehouse (`etl_load_warehouse.py`)

**Schedule**: Daily at 03:00 UTC

**Tasks**:
- `prepare_for_load`: Format data and prepare partitions
- `load_facts_table`: Load fact table data
- `load_dimensions_table`: Load dimension tables
- `refresh_warehouse_views`: Refresh materialized views
- `validate_warehouse_load`: Validate loaded data integrity
- `notify_load_complete`: Send completion notification

**Pattern**: Fan-out to fan-in (parallel loading, sequential validation)

#### Daily Analytics (`daily_analytics.py`)

**Schedule**: Daily at 04:00 UTC

**Tasks**:
- `calculate_kpis`: Calculate key performance indicators
- `generate_customer_analytics`: Analyze customer segments
- `generate_product_analytics`: Analyze product performance
- `generate_trend_analysis`: Generate trends and forecasts
- `generate_report`: Combine analytics into report
- `publish_report`: Distribute to stakeholders
- `send_completion_notification`: Send final notification

**Pattern**: Fan-out to fan-in with sequential publication

## Running Tests

### Unit Tests

Test DAG structure, dependencies, and configurations:

```bash
# Install test dependencies
pip install pytest unittest

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_dag_validation.py -v

# Run with coverage
pip install coverage
coverage run -m pytest tests/
coverage report
```

### Test Files

- **`test_dag_validation.py`**: Validates DAG structure, schedules, owners
- **`test_task_dependencies.py`**: Verifies task dependency chains
- **`test_operator_configurations.py`**: Checks operator parameters and retry policies

### DAG Syntax Check

```bash
# Check DAG syntax (must be inside Airflow container)
docker-compose exec webserver airflow dags list
docker-compose exec webserver airflow dags validate
```

## Configuration

### Environment Variables

Modify `docker-compose.yml` to configure:

```yaml
environment:
  AIRFLOW__CORE__EXECUTOR: CeleryExecutor
  AIRFLOW__CORE__PARALLELISM: 4  # Max parallel DAG runs
  AIRFLOW__CORE__MAX_ACTIVE_TASKS_PER_DAG: 16
  AIRFLOW__CORE__LOG_LEVEL: INFO
```

### Database Configuration

Configure source database and warehouse in Airflow variables or `config/`:

```python
# In Airflow UI or via CLI
airflow variables set SOURCE_DB_HOST source_db.example.com
airflow variables set SOURCE_DB_PORT 5432
airflow variables set SOURCE_DB_NAME source_db
airflow variables set WAREHOUSE_DB_HOST warehouse.example.com
airflow variables set WAREHOUSE_DB_NAME warehouse
```

### Custom Plugins

Add custom operators/hooks to `plugins/` directory:

```
plugins/
├── operators/
│   └── custom_operator.py
├── hooks/
│   └── custom_hook.py
└── __init__.py
```

## Development Workflow

### Adding New DAGs

1. Create DAG file in `src/dags/`:

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'your-name',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 1, 1),
}

dag = DAG(
    'your_dag_name',
    default_args=default_args,
    schedule_interval='0 0 * * *',
    catchup=False,
)

def your_task():
    print("Task executed")

task = PythonOperator(
    task_id='your_task',
    python_callable=your_task,
    dag=dag,
)
```

2. Restart Airflow scheduler:

```bash
docker-compose restart scheduler
```

3. Add tests in `tests/` directory

### Monitoring and Troubleshooting

#### View Logs

```bash
# Webserver logs
docker-compose logs webserver

# Scheduler logs
docker-compose logs scheduler

# Worker logs
docker-compose logs celery_worker_1

# All logs
docker-compose logs -f
```

#### Access Database

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U airflow -d airflow

# Useful queries
SELECT * FROM dag;
SELECT * FROM task_instance WHERE dag_id='etl_extract_data';
```

#### Clear Tasks

```bash
# Clear a DAG run
docker-compose exec webserver airflow dags delete etl_extract_data

# Clear a specific task instance
docker-compose exec webserver airflow tasks clear etl_extract_data -t task_id -d
```

#### Scale Workers

Add more workers by adding to `docker-compose.yml`:

```yaml
celery_worker_3:
  image: apache/airflow:2.7.3
  # ... same config as worker 1/2 ...
```

Then:

```bash
docker-compose up -d celery_worker_3
```

## Common Operations

### Manual DAG Trigger

```bash
# Trigger via Airflow UI at http://localhost:8080

# Or via CLI
docker-compose exec webserver airflow dags trigger etl_extract_data
```

### Backfill Data

```bash
# Run DAG for specific date range
docker-compose exec webserver airflow dags backfill etl_extract_data \
  --start-date 2024-01-01 \
  --end-date 2024-01-31
```

### View Task Logs

```bash
docker-compose exec webserver airflow tasks logs etl_extract_data extract_from_source 2024-01-01
```

## Production Deployment

For production use:

1. **Database**:
   - Use external PostgreSQL instance (RDS, Cloud SQL)
   - Configure connection in `AIRFLOW__DATABASE__SQL_ALCHEMY_CONN`

2. **Message Broker**:
   - Use Redis cluster or AWS ElastiCache
   - Update `AIRFLOW__CELERY__BROKER_URL`

3. **Executor**:
   - Consider KubernetesExecutor for Kubernetes deployments
   - Use CloudComposerExecutor for GCP

4. **Monitoring**:
   - Integrate with Prometheus/Grafana
   - Set up Datadog/New Relic monitoring
   - Configure PagerDuty alerts

5. **Security**:
   - Use RBAC for user management
   - Enable Kerberos/LDAP authentication
   - Implement network policies and encryption

## Stopping Services

```bash
# Stop services (keep volumes)
docker-compose stop

# Stop and remove containers
docker-compose down

# Remove all data
docker-compose down -v
```

## Additional Resources

- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
- [CeleryExecutor Documentation](https://airflow.apache.org/docs/apache-airflow/stable/executor/celery.html)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)

## Support

For issues or questions:

1. Check logs: `docker-compose logs -f [service-name]`
2. Review DAG syntax: `docker-compose exec webserver airflow dags validate`
3. Check Airflow UI for task failures
4. Review test output: `python -m pytest tests/ -v`

## License

See parent project LICENSE file.
