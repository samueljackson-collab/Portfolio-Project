#!/usr/bin/env python3
"""
validate_module.py
==================
Validates the structure and content of the Terraform RDS module at
projects/30-terraform-rds/.

Checks:
  1. Required files in modules/rds/ exist
  2. Expected resource types are present in main.tf
  3. All required outputs are declared in outputs.tf
  4. All required variables are declared in variables.tf
  5. Example entry-point files exist

Usage:
  python3 tests/validate_module.py
  # or from the project root:
  python3 projects/30-terraform-rds/tests/validate_module.py
"""

import os
import re
import sys

# ---------------------------------------------------------------------------
# Resolve paths relative to this script's location
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)   # .../30-terraform-rds/


def project_path(*parts: str) -> str:
    """Return an absolute path under the project root."""
    return os.path.join(PROJECT_ROOT, *parts)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

total_checks = 0
passed_checks = 0


def check(description: str, result: bool, detail: str = "") -> None:
    global total_checks, passed_checks
    total_checks += 1
    if result:
        passed_checks += 1
        print(f"[PASS] {description}")
    else:
        msg = f"[FAIL] {description}"
        if detail:
            msg += f"\n       => {detail}"
        print(msg)


def file_exists(rel_path: str) -> bool:
    return os.path.isfile(project_path(rel_path))


def read_file(rel_path: str) -> str:
    full = project_path(rel_path)
    if not os.path.isfile(full):
        return ""
    with open(full, "r", encoding="utf-8") as fh:
        return fh.read()


def has_resource(content: str, resource_type: str) -> bool:
    """Return True if 'resource "resource_type"' appears in the content."""
    pattern = rf'resource\s+"{ re.escape(resource_type) }"\s+"'
    return bool(re.search(pattern, content))


def has_output(content: str, output_name: str) -> bool:
    """Return True if 'output "output_name"' appears in outputs.tf."""
    pattern = rf'output\s+"{ re.escape(output_name) }"\s+\{{'
    return bool(re.search(pattern, content))


def has_variable(content: str, var_name: str) -> bool:
    """Return True if 'variable "var_name"' appears in variables.tf."""
    pattern = rf'variable\s+"{ re.escape(var_name) }"\s+\{{'
    return bool(re.search(pattern, content))


# ---------------------------------------------------------------------------
# Test definitions
# ---------------------------------------------------------------------------

REQUIRED_MODULE_FILES = [
    "modules/rds/main.tf",
    "modules/rds/variables.tf",
    "modules/rds/outputs.tf",
    "modules/rds/versions.tf",
]

REQUIRED_RESOURCES = [
    "aws_db_instance",
    "aws_db_subnet_group",
    "aws_security_group",
    "aws_cloudwatch_metric_alarm",
    "aws_secretsmanager_secret",
    "aws_db_parameter_group",
    "aws_iam_role",
]

REQUIRED_OUTPUTS = [
    "db_instance_endpoint",
    "db_instance_port",
    "db_instance_id",
    "db_instance_arn",
    "db_subnet_group_name",
    "security_group_id",
    "secret_arn",
]

REQUIRED_VARIABLES = [
    "identifier",
    "engine",
    "engine_version",
    "instance_class",
    "allocated_storage",
    "max_allocated_storage",
    "db_name",
    "username",
    "vpc_id",
    "subnet_ids",
    "app_security_group_ids",
    "multi_az",
    "backup_retention_period",
    "backup_window",
    "maintenance_window",
    "deletion_protection",
    "skip_final_snapshot",
    "tags",
]

REQUIRED_EXAMPLE_FILES = [
    "examples/postgres/main.tf",
    "examples/mysql/main.tf",
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print("=== Terraform RDS Module Validation ===")
    print(f"Project root: {PROJECT_ROOT}\n")

    # 1. Required module files exist
    for rel_path in REQUIRED_MODULE_FILES:
        check(f"{rel_path} exists", file_exists(rel_path))

    print()

    # 2. Resource types in main.tf
    main_tf = read_file("modules/rds/main.tf")
    for resource_type in REQUIRED_RESOURCES:
        check(
            f"{resource_type} resource found in main.tf",
            has_resource(main_tf, resource_type),
            f"Pattern: resource \"{resource_type}\" not found",
        )

    print()

    # 3. Outputs
    outputs_tf = read_file("modules/rds/outputs.tf")
    for output_name in REQUIRED_OUTPUTS:
        check(
            f"Output '{output_name}' defined",
            has_output(outputs_tf, output_name),
        )

    print()

    # 4. Variables
    variables_tf = read_file("modules/rds/variables.tf")
    all_vars_present = all(has_variable(variables_tf, v) for v in REQUIRED_VARIABLES)
    missing = [v for v in REQUIRED_VARIABLES if not has_variable(variables_tf, v)]
    check(
        f"All {len(REQUIRED_VARIABLES)} required variables defined",
        all_vars_present,
        f"Missing: {missing}" if missing else "",
    )

    print()

    # 5. Example files exist
    for rel_path in REQUIRED_EXAMPLE_FILES:
        check(f"{rel_path} exists", file_exists(rel_path))

    # 6. versions.tf has minimum Terraform version constraint
    versions_tf = read_file("modules/rds/versions.tf")
    has_tf_version = bool(re.search(r'required_version\s*=', versions_tf))
    check("versions.tf contains required_version constraint", has_tf_version)

    has_aws_provider = bool(re.search(r'"hashicorp/aws"', versions_tf))
    check("versions.tf specifies hashicorp/aws provider", has_aws_provider)

    print()
    print("==========================================")
    print(f"{passed_checks}/{total_checks} checks passed")

    return 0 if passed_checks == total_checks else 1


if __name__ == "__main__":
    sys.exit(main())
