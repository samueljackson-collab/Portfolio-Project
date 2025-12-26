#!/usr/bin/env python3
"""MASTER_FACTORY generator and validator.

This script can generate per-project `MASTER_FACTORY.md` playbooks and, optionally,
scaffold CI workflows, IaC skeletons, and test harnesses that align to each
project's technology stack. It also includes a validation mode to ensure required
sections and artifacts exist before a release.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional
import argparse
import sys

MASTER_FACTORY_FILENAME = "MASTER_FACTORY.md"


@dataclass
class ArtifactSpec:
    """Specification for an artifact to scaffold."""

    path: Path
    prompt: str
    template: str

    def resolved_path(self, base_dir: Path) -> Path:
        return base_dir / self.path


@dataclass
class ProjectSpec:
    """Specification for a project in the master factory."""

    slug: str
    name: str
    description: str
    tech_stack: List[str]
    ci: ArtifactSpec
    iac: ArtifactSpec
    tests: ArtifactSpec

    def project_root(self, base_dir: Path) -> Path:
        return base_dir / self.slug


DEFAULT_PROJECTS: List[ProjectSpec] = [
    ProjectSpec(
        slug="projects/01-sde-devops",
        name="DevOps Delivery",
        description="API + infrastructure delivery track that leans on Terraform and pytest smoke tests.",
        tech_stack=["Python", "FastAPI", "Terraform", "GitHub Actions", "pytest"],
        ci=ArtifactSpec(
            path=Path(".github/workflows/devops-delivery.yml"),
            prompt=(
                "GitHub Actions pipeline that builds the FastAPI service, runs unit tests, "
                "validates Terraform with fmt/validate/plan, and publishes artifacts to the registry."
            ),
            template="""name: DevOps Delivery CI

on:
  push:
    branches: ["main"]
  pull_request:

jobs:
  build-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run unit tests
        run: pytest -q

  terraform-validate:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: projects/01-sde-devops/infrastructure/terraform
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
      - name: Terraform fmt
        run: terraform fmt -check
      - name: Terraform validate
        run: terraform validate
      - name: Terraform plan
        run: terraform plan -input=false -lock=false
""",
        ),
        iac=ArtifactSpec(
            path=Path("projects/01-sde-devops/infrastructure/terraform/main.tf"),
            prompt=(
                "Terraform entrypoint defining providers, remote state, and a base module call."
            ),
            template="""terraform {
  required_version = ">= 1.6"
  backend "local" {}
}

provider "aws" {
  region = var.region
}

module "service" {
  source = "./modules/service"
  # TODO: wire inputs for VPC, ECS, and RDS
}
""",
        ),
        tests=ArtifactSpec(
            path=Path("projects/01-sde-devops/tests/test_smoke.py"),
            prompt="pytest smoke tests that hit the health endpoint and assert Terraform outputs are wired.",
            template="""import requests

def test_healthcheck():
    response = requests.get("http://localhost:8000/health")
    assert response.status_code == 200
    assert response.json().get("status") == "ok"
""",
        ),
    ),
    ProjectSpec(
        slug="projects/02-cloud-architecture",
        name="Serverless Reference",
        description="Serverless APIs backed by AWS SAM with GitHub Actions and integration tests.",
        tech_stack=["AWS SAM", "API Gateway", "Lambda", "GitHub Actions", "pytest"],
        ci=ArtifactSpec(
            path=Path(".github/workflows/sam-reference.yml"),
            prompt=(
                "GitHub Actions workflow that runs `sam validate`, builds the template, runs unit/integration tests, "
                "and packages artifacts to S3."
            ),
            template="""name: SAM Reference CI

on:
  push:
    branches: ["main"]
  pull_request:

jobs:
  sam-validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/setup-sam@v2
      - name: SAM Validate
        run: sam validate -t projects/02-cloud-architecture/template.yaml
      - name: SAM Build
        run: sam build -t projects/02-cloud-architecture/template.yaml
      - name: SAM Package (dry-run)
        run: sam package --s3-bucket example-bucket --s3-prefix sam-reference --template-file .aws-sam/build/template.yaml --output-template-file packaged.yaml --no-execute-changeset
""",
        ),
        iac=ArtifactSpec(
            path=Path("projects/02-cloud-architecture/template.yaml"),
            prompt="AWS SAM template describing API Gateway + Lambda skeleton with tracing and logging enabled.",
            template="""AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Serverless reference stack

Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: app.lambda_handler
      Runtime: python3.11
      CodeUri: src/
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /health
            Method: get
""",
        ),
        tests=ArtifactSpec(
            path=Path("projects/02-cloud-architecture/tests/test_api.py"),
            prompt="pytest integration tests invoking the SAM local API and asserting request/response contracts.",
            template="""import requests

def test_health_endpoint():
    response = requests.get("http://127.0.0.1:3000/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
""",
        ),
    ),
    ProjectSpec(
        slug="projects/04-qa-testing",
        name="Quality Automation",
        description="Frontend + API regression suite powered by Playwright.",
        tech_stack=["TypeScript", "Playwright", "GitHub Actions"],
        ci=ArtifactSpec(
            path=Path(".github/workflows/playwright-regression.yml"),
            prompt="GitHub Actions workflow that installs Node, caches npm, runs Playwright tests headlessly, and uploads traces.",
            template="""name: Playwright Regression

on:
  push:
    branches: ["main"]
  pull_request:

jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install dependencies
        run: cd projects/04-qa-testing && npm install
      - name: Run Playwright tests
        run: cd projects/04-qa-testing && npx playwright test --reporter=line
      - name: Upload Playwright artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: projects/04-qa-testing/playwright-report
""",
        ),
        iac=ArtifactSpec(
            path=Path("projects/04-qa-testing/infrastructure/terraform/main.tf"),
            prompt="Terraform workspace that provisions ephemeral test runners and secrets for Playwright.",
            template="""terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

variable "region" {
  type = string
  default = "us-east-1"
}

resource "aws_secretsmanager_secret" "playwright_api" {
  name = "playwright/api-key"
}
""",
        ),
        tests=ArtifactSpec(
            path=Path("projects/04-qa-testing/tests/playwright.config.ts"),
            prompt="Playwright configuration enabling trace collection and parallel regression suites.",
            template="""import { defineConfig } from '@playwright/test';

export default defineConfig({
  timeout: 60000,
  use: {
    trace: 'on-first-retry',
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
  },
  projects: [{ name: 'chromium', use: { browserName: 'chromium' } }],
});
""",
        ),
    ),
    ProjectSpec(
        slug="projects/p07-roaming-simulation",
        name="International Roaming Simulation",
        description=(
            "Python roaming simulator with mock HLR/HSS, roaming state machine, and pytest scenarios."
            " Includes metrics/packet-capture hooks for observability."
        ),
        tech_stack=["Python", "Pytest", "Requests", "Makefile", "GitHub Actions"],
        ci=ArtifactSpec(
            path=Path(".github/workflows/p07-roaming-simulation.yml"),
            prompt=(
                "GitHub Actions pipeline that sets up Python, installs dev dependencies, "
                "runs lint + pytest suites (unit/integration/e2e) with coverage, and publishes HTML reports."
            ),
            template="""name: P07 Roaming Simulation CI

on:
  push:
    branches: ["main"]
  pull_request:

jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r projects/p07-roaming-simulation/requirements-dev.txt
      - name: Run pytest suites
        run: |
          cd projects/p07-roaming-simulation
          pytest -m "not slow" --cov=src --cov-report=xml --cov-report=term-missing
      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: roaming-coverage
          path: projects/p07-roaming-simulation/coverage.xml
""",
        ),
        iac=ArtifactSpec(
            path=Path("projects/p07-roaming-simulation/infrastructure/terraform/main.tf"),
            prompt=(
                "Terraform skeleton for ephemeral roaming lab (VPC, subnet, and EC2 runner) "
                "to execute packet-capture simulations."
            ),
            template="""terraform {
  required_version = ">= 1.6"
}

provider "aws" {
  region = var.region
}

resource "aws_vpc" "roaming_lab" {
  cidr_block = var.cidr_block
  tags = {
    Name = "roaming-lab"
  }
}
""",
        ),
        tests=ArtifactSpec(
            path=Path("projects/p07-roaming-simulation/tests/test_roaming_factory.py"),
            prompt=(
                "Pytest harness that bootstraps the roaming simulator with sample subscribers and asserts "
                "attach/detach flows plus roaming billing triggers."
            ),
            template="""import pytest

from src.roaming import Simulator


@pytest.fixture()
def simulator():
    return Simulator.from_example_config()


def test_attach_and_detach(simulator: Simulator):
    subscriber = "001010123456789"
    result = simulator.attach(subscriber)
    assert result.accepted is True
    assert simulator.detach(subscriber).accepted is True
""",
        ),
    ),
    ProjectSpec(
        slug="projects/p08-api-testing",
        name="Backend API Testing",
        description=(
            "Postman collections with Newman CLI harness for REST API validation, JSON schema contracts, and latency checks."
        ),
        tech_stack=["Node.js", "Postman", "Newman", "JSON Schema", "GitHub Actions"],
        ci=ArtifactSpec(
            path=Path(".github/workflows/p08-api-testing.yml"),
            prompt=(
                "GitHub Actions workflow that installs Node, caches npm, runs Newman against the core collection with "
                "environment files, and publishes HTML reports."
            ),
            template="""name: P08 API Testing CI

on:
  push:
    branches: ["main"]
  pull_request:

jobs:
  newman:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Install newman
        run: npm install -g newman newman-reporter-htmlextra
      - name: Run collection
        run: |
          newman run projects/p08-api-testing/collections/core.postman_collection.json \
            -e projects/p08-api-testing/environments/local.postman_environment.json \
            --reporters htmlextra --reporter-htmlextra-export newman-report.html
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: newman-report
          path: newman-report.html
""",
        ),
        iac=ArtifactSpec(
            path=Path("projects/p08-api-testing/infrastructure/docker-compose.yml"),
            prompt=(
                "Docker Compose harness to launch a mock API under test plus the Newman runner container for smoke checks."
            ),
            template="""version: '3.9'
services:
  mock-api:
    image: mockserver/mockserver:5.15.0
    ports:
      - "1080:1080"

  newman-runner:
    image: postman/newman:alpine
    entrypoint: ["tail", "-f", "/dev/null"]
""",
        ),
        tests=ArtifactSpec(
            path=Path("projects/p08-api-testing/tests/contract_smoke.postman_collection.json"),
            prompt="Postman collection focused on schema/contract validation for auth and core resources.",
            template="""{
  "info": {"name": "Contract Smoke", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"},
  "item": [
    {
      "name": "Health",
      "request": {"method": "GET", "url": "{{base_url}}/health"},
      "event": [{"listen": "test", "script": {"exec": [
        "pm.test('status', () => pm.response.to.have.status(200));",
        "pm.test('payload', () => pm.expect(pm.response.json()).to.have.property('status', 'ok'));"
      ]}}]
    }
  ]
}
""",
        ),
    ),
    ProjectSpec(
        slug="projects/p09-cloud-native-poc",
        name="Cloud-Native POC",
        description="FastAPI app with Docker assets and pytest coverage exceeding 90%.",
        tech_stack=["Python", "FastAPI", "Docker", "Pytest", "GitHub Actions"],
        ci=ArtifactSpec(
            path=Path(".github/workflows/p09-cloud-native-poc.yml"),
            prompt=(
                "GitHub Actions pipeline that builds the FastAPI image, runs pytest with coverage, and performs a docker-compose "
                "smoke to hit /health."
            ),
            template="""name: P09 Cloud Native CI

on:
  push:
    branches: ["main"]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install deps
        run: |
          cd projects/p09-cloud-native-poc
          pip install -r requirements.txt
      - name: Run unit tests
        run: |
          cd projects/p09-cloud-native-poc
          pytest --cov=app --cov-report=term-missing
  docker-smoke:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - name: Build image
        run: docker build -t cloud-native-poc projects/p09-cloud-native-poc
      - name: Compose up
        run: |
          cd projects/p09-cloud-native-poc
          docker compose up -d
          # Poll for service readiness
          for i in {1..15}; do
            if curl -sf http://localhost:8000/health > /dev/null; then
              echo "Service is healthy."
              exit 0
            fi
            echo "Waiting for service... ($i/15)"
            sleep 2
          done
          echo "Error: Service failed to start in time."
          exit 1
""",
        ),
        iac=ArtifactSpec(
            path=Path("projects/p09-cloud-native-poc/infrastructure/kubernetes/deployment.yaml"),
            prompt="Kubernetes manifest for deploying the FastAPI service with liveness/readiness probes.",
            template="""apiVersion: apps/v1
kind: Deployment
metadata:
  name: cloud-native-poc
spec:
  replicas: 2
  selector:
    matchLabels:
      app: cloud-native-poc
  template:
    metadata:
      labels:
        app: cloud-native-poc
    spec:
      containers:
        - name: api
          image: ghcr.io/example/cloud-native-poc:latest
          ports:
            - containerPort: 8000
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
""",
        ),
        tests=ArtifactSpec(
            path=Path("projects/p09-cloud-native-poc/tests/test_health_factory.py"),
            prompt="Pytest smoke covering /health and /ready endpoints for the FastAPI POC.",
            template="""from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json().get("status") == "ok"
""",
        ),
    ),
    ProjectSpec(
        slug="projects/p10-multi-region",
        name="Multi-Region Architecture",
        description=(
            "Active/passive AWS deployment with Route 53 failover, cross-region RDS replicas, and automated failover drills."
        ),
        tech_stack=["AWS", "Route 53", "CloudFormation", "RDS", "Bash"],
        ci=ArtifactSpec(
            path=Path(".github/workflows/p10-multi-region.yml"),
            prompt=(
                "GitHub Actions workflow that lint/validates CloudFormation templates, runs failover simulation scripts, "
                "and surfaces Route 53 health check results."
            ),
            template="""name: P10 Multi-Region CI

on:
  push:
    branches: ["main"]
  pull_request:

jobs:
  cfn-validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: scottbrenner/cfn-lint-action@v2
        with:
          template_files: projects/p10-multi-region/infrastructure/cloudformation/stack-set.yaml
  failover-drill:
    runs-on: ubuntu-latest
    needs: cfn-validate
    steps:
      - uses: actions/checkout@v4
      - name: Run failover simulation
        run: |
          cd projects/p10-multi-region
          bash scripts/failover_simulation.sh
""",
        ),
        iac=ArtifactSpec(
            path=Path("projects/p10-multi-region/infrastructure/cloudformation/stack-set.yaml"),
            prompt="CloudFormation StackSet defining primary/secondary region resources with Route 53 health checks.",
            template="""AWSTemplateFormatVersion: '2010-09-09'
Description: Multi-region stack set skeleton
Resources:
  DNSFailoverHealthCheck:
    Type: AWS::Route53::HealthCheck
    Properties:
      HealthCheckConfig:
        Type: HTTPS
        FullyQualifiedDomainName: example.com
        RequestInterval: 30
        FailureThreshold: 3
""",
        ),
        tests=ArtifactSpec(
            path=Path("projects/p10-multi-region/tests/test_failover_factory.py"),
            prompt="Pytest harness that mocks Route 53 health responses and asserts failover orchestration logic.",
            template="""def test_failover_triggers_secondary(monkeypatch):
    from .. import failover

    monkeypatch.setattr(failover, "is_primary_healthy", lambda: False)
    monkeypatch.setattr(failover, "promote_secondary", lambda: "promoted")

    assert failover.orchestrate() == "promoted"
""",
        ),
    ),
    ProjectSpec(
        slug="projects/p11-serverless",
        name="API Gateway & Serverless",
        description="SAM-driven serverless API with Lambda handlers, API Gateway routing, DynamoDB, and tracing hooks.",
        tech_stack=["AWS SAM", "Lambda", "API Gateway", "DynamoDB", "Python"],
        ci=ArtifactSpec(
            path=Path(".github/workflows/p11-serverless.yml"),
            prompt=(
                "GitHub Actions workflow that runs `sam validate`, builds the template, executes unit tests, "
                "and performs `sam local start-api` smoke checks."
            ),
            template="""name: P11 Serverless CI

on:
  push:
    branches: ["main"]
  pull_request:

jobs:
  sam-validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/setup-sam@v2
      - name: SAM Validate
        run: sam validate -t projects/p11-serverless/template.yaml
      - name: SAM Build
        run: sam build -t projects/p11-serverless/template.yaml
      - name: Run unit tests
        run: |
          cd projects/p11-serverless
          pytest -q
""",
        ),
        iac=ArtifactSpec(
            path=Path("projects/p11-serverless/template.yaml"),
            prompt="AWS SAM template for API Gateway, Lambda CRUD handlers, DynamoDB table, and tracing defaults.",
            template="""AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Serverless API skeleton
Resources:
  ApiFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: app.lambda_handler
      Runtime: python3.11
      CodeUri: src/
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /health
            Method: get
  DataTable:
    Type: AWS::DynamoDB::Table
    Properties:
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: pk
          AttributeType: S
      KeySchema:
        - AttributeName: pk
          KeyType: HASH
""",
        ),
        tests=ArtifactSpec(
            path=Path("projects/p11-serverless/tests/test_health_factory.py"),
            prompt="Pytest case invoking the /health Lambda handler and asserting observability fields.",
            template="""from app import app


def test_health_handler_returns_ok():
    result = app.lambda_handler({"path": "/health"}, None)
    assert result["statusCode"] == 200
    assert result["body"] == '{"status": "ok"}'
""",
        ),
    ),
    ProjectSpec(
        slug="projects/p12-data-pipeline",
        name="Data Pipeline (Airflow)",
        description="Dockerized Apache Airflow stack with ETL DAGs and promotion-ready QA artifacts.",
        tech_stack=["Apache Airflow", "Docker Compose", "PostgreSQL", "pytest", "GitHub Actions"],
        ci=ArtifactSpec(
            path=Path(".github/workflows/p12-data-pipeline.yml"),
            prompt=(
                "GitHub Actions workflow that lints DAGs, runs pytest-based DAG validation, and executes an Airflow docker-compose "
                "smoke to ensure scheduler/webserver start."
            ),
            template="""name: P12 Data Pipeline CI

on:
  push:
    branches: ["main"]
  pull_request:

jobs:
  dag-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install deps
        run: |
          cd projects/p12-data-pipeline
          pip install -r requirements.txt
      - name: Lint DAGs
        run: |
          cd projects/p12-data-pipeline
          python -m compileall dags
      - name: Run DAG tests
        run: |
          cd projects/p12-data-pipeline
          pytest -q
""",
        ),
        iac=ArtifactSpec(
            path=Path("projects/p12-data-pipeline/docker-compose.yml"),
            prompt="Docker Compose stack to run Airflow scheduler, webserver, and PostgreSQL metadata DB.",
            template="""version: '3.9'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-airflow}
      POSTGRES_DB: airflow
  airflow:
    image: apache/airflow:2.8
    depends_on:
      - postgres
    environment:
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:${POSTGRES_PASSWORD:-airflow}@postgres/airflow
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
    command: ["airflow", "webserver"]
""",
        ),
        tests=ArtifactSpec(
            path=Path("projects/p12-data-pipeline/tests/test_dag_factory.py"),
            prompt="Pytest DAG validation ensuring DAGs load and critical tasks are present before promotion.",
            template="""from airflow.models import DagBag


def test_dags_import_cleanly():
    dag_bag = DagBag(dag_folder="dags", include_examples=False)
    assert not dag_bag.import_errors
    assert dag_bag.dags
""",
        ),
    ),
]


REQUIRED_SECTIONS = [
    "## Overview",
    "## Tech Stack",
    "## CI Workflow",
    "## Infrastructure as Code",
    "## Test Harness",
    "## Release Validation Checklist",
]


def generate_master_factory(project: ProjectSpec, base_dir: Path, scaffold_ci: bool, scaffold_iac: bool, scaffold_tests: bool, overwrite: bool) -> Path:
    """
    Generate a MASTER_FACTORY.md playbook for a given project, and optionally scaffold CI, IaC, and test artifacts.

    Parameters:
        project (ProjectSpec): The project specification containing metadata and artifact specs.
        base_dir (Path): The base directory in which to create project files.
        scaffold_ci (bool): If True, scaffold the CI workflow artifact.
        scaffold_iac (bool): If True, scaffold the Infrastructure as Code artifact.
        scaffold_tests (bool): If True, scaffold the test harness artifact.
        overwrite (bool): If True, overwrite existing files; otherwise, skip writing if files exist.

    Returns:
        Path: The path to the generated MASTER_FACTORY.md file.

    Side Effects:
        - Creates directories and files for the project and its artifacts.
        - Writes to the console (stdout) to indicate actions taken.
    """
    project_root = project.project_root(base_dir)
    project_root.mkdir(parents=True, exist_ok=True)
    master_factory_path = project_root / MASTER_FACTORY_FILENAME

    content = _render_master_factory_content(project)
    if master_factory_path.exists() and not overwrite:
        print(f"Skipping write for {master_factory_path} (exists, use --overwrite to replace)")
    else:
        master_factory_path.write_text(content)
        print(f"Wrote {master_factory_path}")

    if scaffold_ci:
        _scaffold_artifact(project.ci, base_dir, overwrite)
    if scaffold_iac:
        _scaffold_artifact(project.iac, base_dir, overwrite)
    if scaffold_tests:
        _scaffold_artifact(project.tests, base_dir, overwrite)

    return master_factory_path


def _scaffold_artifact(spec: ArtifactSpec, base_dir: Path, overwrite: bool) -> None:
    file_path = spec.resolved_path(base_dir)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if file_path.exists() and not overwrite:
        print(f"Skipping scaffold for {file_path} (exists, use --overwrite to replace)")
        return

    header = f"# {file_path.name}\n\n"
    body = f"<!-- Prompt: {spec.prompt} -->\n\n{spec.template.strip()}\n"
    file_path.write_text(header + body)
    print(f"Scaffolded {file_path}")


def _render_master_factory_content(project: ProjectSpec) -> str:
    tech_stack = "\n".join(f"- {item}" for item in project.tech_stack)

    return f"""# {project.name} MASTER_FACTORY

## Overview
{project.description}

## Tech Stack
{tech_stack}

## CI Workflow
- Path: `{project.ci.path}`
- Prompt: {project.ci.prompt}

## Infrastructure as Code
- Path: `{project.iac.path}`
- Prompt: {project.iac.prompt}

## Test Harness
- Path: `{project.tests.path}`
- Prompt: {project.tests.prompt}

## Release Validation Checklist
- [ ] `MASTER_FACTORY.md` includes all sections and up-to-date prompts
- [ ] CI workflow exists at `{project.ci.path}`
- [ ] IaC skeleton exists at `{project.iac.path}`
- [ ] Test harness exists at `{project.tests.path}`
"""


def validate_projects(projects: Iterable[ProjectSpec], base_dir: Path) -> int:
    failures = 0
    for project in projects:
        master_factory_path = project.project_root(base_dir) / MASTER_FACTORY_FILENAME
        issues = _validate_project(master_factory_path, project, base_dir)
        if issues:
            failures += 1
            print(f"\n[INVALID] {project.name} ({project.slug}):")
            for issue in issues:
                print(f" - {issue}")
        else:
            print(f"[OK] {project.name} ({project.slug})")
    return failures


def _validate_project(master_factory_path: Path, project: ProjectSpec, base_dir: Path) -> List[str]:
    issues: List[str] = []
    if not master_factory_path.exists():
        issues.append(f"Missing {MASTER_FACTORY_FILENAME} at {master_factory_path}")
        return issues

    content = master_factory_path.read_text()

    for section in REQUIRED_SECTIONS:
        if section not in content:
            issues.append(f"Section '{section}' missing from {master_factory_path}")

    expected_paths = [project.ci.path, project.iac.path, project.tests.path]
    for expected_path in expected_paths:
        if str(expected_path) not in content:
            issues.append(f"Path '{expected_path}' not referenced in {master_factory_path}")

    artifacts = [project.ci, project.iac, project.tests]
    for artifact in artifacts:
        if not artifact.resolved_path(base_dir).exists():
            issues.append(f"Artifact missing: {artifact.resolved_path(base_dir)}")

    return issues


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate or validate MASTER_FACTORY assets.")
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root (defaults to repo root relative to this script).",
    )
    parser.add_argument(
        "--project",
        action="append",
        dest="projects",
        help="Limit generation/validation to specific project slugs (matches 'slug' field).",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files when scaffolding.")
    parser.add_argument("--scaffold-ci", action="store_true", help="Generate CI workflow files during creation.")
    parser.add_argument("--scaffold-iac", action="store_true", help="Generate IaC skeletons during creation.")
    parser.add_argument("--scaffold-tests", action="store_true", help="Generate test harness files during creation.")
    parser.add_argument("--validate", action="store_true", help="Run validation mode instead of generation.")
    return parser.parse_args(argv)


def _filter_projects(projects: List[ProjectSpec], selected: Optional[List[str]]) -> List[ProjectSpec]:
    if not selected:
        return projects
    selected_set = set(selected)
    return [project for project in projects if project.slug in selected_set]


def main(argv: Optional[List[str]] = None) -> int:
    args = _parse_args(argv)
    base_dir: Path = args.base_dir
    projects = _filter_projects(DEFAULT_PROJECTS, args.projects)

    if not projects:
        print("No projects matched the provided filters.")
        return 1

    if args.validate:
        failures = validate_projects(projects, base_dir)
        if failures:
            print(f"\nValidation failed for {failures} project(s).")
            return 1
        print("All projects passed validation.")
        return 0

    for project in projects:
        generate_master_factory(
            project,
            base_dir=base_dir,
            scaffold_ci=args.scaffold_ci,
            scaffold_iac=args.scaffold_iac,
            scaffold_tests=args.scaffold_tests,
            overwrite=args.overwrite,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
