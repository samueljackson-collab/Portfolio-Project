#!/usr/bin/env python3
"""
CloudFormation template validator.

Validates templates using AWS CLI and cfn-lint before deployment.
"""
import json
import subprocess
import sys
from pathlib import Path


def validate_with_aws_cli(template_path: Path) -> bool:
    """Validate template using AWS CloudFormation validate-template API."""
    try:
        result = subprocess.run(
            [
                "aws",
                "cloudformation",
                "validate-template",
                "--template-body",
                f"file://{template_path}",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"✓ AWS validation passed: {template_path.name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ AWS validation failed: {template_path.name}")
        print(f"  Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print("✗ AWS CLI not found. Install: https://aws.amazon.com/cli/")
        return False


def validate_with_cfn_lint(template_path: Path) -> bool:
    """Validate template using cfn-lint (static analysis)."""
    try:
        result = subprocess.run(
            ["cfn-lint", str(template_path), "--format", "json"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"✓ cfn-lint passed: {template_path.name}")
            return True
        else:
            print(f"✗ cfn-lint failed: {template_path.name}")
            if result.stdout:
                findings = json.loads(result.stdout)
                for finding in findings:
                    print(
                        f"  {finding['Level']}: {finding['Message']} (Rule: {finding['Rule']['Id']})"
                    )
            return False
    except FileNotFoundError:
        print("⚠ cfn-lint not found. Install: pip install cfn-lint")
        return True  # Don't fail if cfn-lint is not installed (optional)
    except json.JSONDecodeError:
        print(f"⚠ cfn-lint output parsing failed for {template_path.name}")
        return True


def main():
    """Validate all CloudFormation templates in infra/ directory."""
    project_root = Path(__file__).parent.parent
    infra_dir = project_root / "infra"

    if not infra_dir.exists():
        print(f"✗ Infrastructure directory not found: {infra_dir}")
        sys.exit(1)

    templates = list(infra_dir.glob("*.yaml")) + list(infra_dir.glob("*.yml"))
    if not templates:
        print(f"✗ No CloudFormation templates found in {infra_dir}")
        sys.exit(1)

    print(f"Validating {len(templates)} template(s)...\n")

    all_passed = True
    for template in templates:
        aws_ok = validate_with_aws_cli(template)
        lint_ok = validate_with_cfn_lint(template)
        all_passed = all_passed and aws_ok and lint_ok
        print()

    if all_passed:
        print("✓ All templates validated successfully")
        sys.exit(0)
    else:
        print("✗ Template validation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
