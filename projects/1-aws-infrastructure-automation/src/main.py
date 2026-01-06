#!/usr/bin/env python3
"""
AWS Infrastructure Automation CLI

A command-line tool for managing AWS infrastructure using Terraform,
AWS CDK, and Pulumi. Provides unified interface for common operations
like planning, deploying, validating, and destroying infrastructure.
"""

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class IaCTool(Enum):
    """Supported Infrastructure as Code tools."""
    TERRAFORM = "terraform"
    CDK = "cdk"
    PULUMI = "pulumi"


class Environment(Enum):
    """Deployment environments."""
    DEV = "dev"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class InfraConfig:
    """Infrastructure configuration."""
    tool: IaCTool
    environment: Environment
    region: str
    project_root: Path
    dry_run: bool = False
    auto_approve: bool = False


class InfrastructureManager:
    """Manages infrastructure operations across different IaC tools."""

    def __init__(self, config: InfraConfig):
        self.config = config
        self.terraform_dir = config.project_root / "terraform"
        self.cdk_dir = config.project_root / "cdk"
        self.pulumi_dir = config.project_root / "pulumi"

    def validate(self) -> bool:
        """Validate infrastructure configuration."""
        print(f"Validating {self.config.tool.value} configuration...")

        if self.config.tool == IaCTool.TERRAFORM:
            return self._validate_terraform()
        elif self.config.tool == IaCTool.CDK:
            return self._validate_cdk()
        elif self.config.tool == IaCTool.PULUMI:
            return self._validate_pulumi()
        return False

    def plan(self) -> bool:
        """Generate execution plan."""
        print(f"Planning {self.config.tool.value} changes for {self.config.environment.value}...")

        if self.config.tool == IaCTool.TERRAFORM:
            return self._plan_terraform()
        elif self.config.tool == IaCTool.CDK:
            return self._plan_cdk()
        elif self.config.tool == IaCTool.PULUMI:
            return self._plan_pulumi()
        return False

    def deploy(self) -> bool:
        """Deploy infrastructure."""
        if not self.config.auto_approve:
            confirm = input(f"Deploy to {self.config.environment.value}? [y/N]: ")
            if confirm.lower() != 'y':
                print("Deployment cancelled.")
                return False

        print(f"Deploying {self.config.tool.value} to {self.config.environment.value}...")

        if self.config.dry_run:
            print("[DRY RUN] Would deploy infrastructure")
            return True

        if self.config.tool == IaCTool.TERRAFORM:
            return self._deploy_terraform()
        elif self.config.tool == IaCTool.CDK:
            return self._deploy_cdk()
        elif self.config.tool == IaCTool.PULUMI:
            return self._deploy_pulumi()
        return False

    def destroy(self) -> bool:
        """Destroy infrastructure."""
        if self.config.environment == Environment.PRODUCTION:
            print("WARNING: Destroying production infrastructure!")
            confirm = input("Type 'destroy-production' to confirm: ")
            if confirm != 'destroy-production':
                print("Destruction cancelled.")
                return False
        elif not self.config.auto_approve:
            confirm = input(f"Destroy {self.config.environment.value} infrastructure? [y/N]: ")
            if confirm.lower() != 'y':
                print("Destruction cancelled.")
                return False

        print(f"Destroying {self.config.tool.value} infrastructure in {self.config.environment.value}...")

        if self.config.dry_run:
            print("[DRY RUN] Would destroy infrastructure")
            return True

        if self.config.tool == IaCTool.TERRAFORM:
            return self._destroy_terraform()
        elif self.config.tool == IaCTool.CDK:
            return self._destroy_cdk()
        elif self.config.tool == IaCTool.PULUMI:
            return self._destroy_pulumi()
        return False

    def output(self) -> dict:
        """Get infrastructure outputs."""
        print(f"Fetching {self.config.tool.value} outputs...")

        if self.config.tool == IaCTool.TERRAFORM:
            return self._output_terraform()
        elif self.config.tool == IaCTool.CDK:
            return self._output_cdk()
        elif self.config.tool == IaCTool.PULUMI:
            return self._output_pulumi()
        return {}

    def cost_estimate(self) -> Optional[dict]:
        """Estimate infrastructure costs using Infracost."""
        print("Estimating infrastructure costs...")

        if self.config.tool != IaCTool.TERRAFORM:
            print("Cost estimation currently only supports Terraform")
            return None

        try:
            result = subprocess.run(
                ["infracost", "breakdown", "--path", str(self.terraform_dir), "--format", "json"],
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except FileNotFoundError:
            print("Infracost not installed. Install with: brew install infracost")
            return None
        except subprocess.CalledProcessError as e:
            print(f"Cost estimation failed: {e.stderr}")
            return None

    # Terraform operations
    def _validate_terraform(self) -> bool:
        """Validate Terraform configuration."""
        try:
            subprocess.run(
                ["terraform", "init", "-backend=false"],
                cwd=self.terraform_dir,
                check=True,
                capture_output=True
            )
            subprocess.run(
                ["terraform", "validate"],
                cwd=self.terraform_dir,
                check=True
            )
            subprocess.run(
                ["terraform", "fmt", "-check", "-recursive"],
                cwd=self.terraform_dir,
                check=True
            )
            print("✓ Terraform configuration is valid")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Terraform validation failed: {e}")
            return False

    def _plan_terraform(self) -> bool:
        """Generate Terraform plan."""
        tfvars_file = self.terraform_dir / f"{self.config.environment.value}.tfvars"

        try:
            subprocess.run(
                ["terraform", "init"],
                cwd=self.terraform_dir,
                check=True
            )

            cmd = ["terraform", "plan", "-out=tfplan"]
            if tfvars_file.exists():
                cmd.extend(["-var-file", str(tfvars_file)])

            subprocess.run(cmd, cwd=self.terraform_dir, check=True)
            print("✓ Terraform plan generated: tfplan")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Terraform plan failed: {e}")
            return False

    def _deploy_terraform(self) -> bool:
        """Apply Terraform configuration."""
        try:
            subprocess.run(
                ["terraform", "apply", "tfplan"],
                cwd=self.terraform_dir,
                check=True
            )
            print("✓ Terraform apply completed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Terraform apply failed: {e}")
            return False

    def _destroy_terraform(self) -> bool:
        """Destroy Terraform infrastructure."""
        tfvars_file = self.terraform_dir / f"{self.config.environment.value}.tfvars"

        try:
            cmd = ["terraform", "destroy", "-auto-approve"]
            if tfvars_file.exists():
                cmd.extend(["-var-file", str(tfvars_file)])

            subprocess.run(cmd, cwd=self.terraform_dir, check=True)
            print("✓ Terraform destroy completed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Terraform destroy failed: {e}")
            return False

    def _output_terraform(self) -> dict:
        """Get Terraform outputs."""
        try:
            result = subprocess.run(
                ["terraform", "output", "-json"],
                cwd=self.terraform_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError:
            return {}

    # CDK operations
    def _validate_cdk(self) -> bool:
        """Validate CDK configuration."""
        try:
            subprocess.run(
                ["cdk", "synth", "--quiet"],
                cwd=self.cdk_dir,
                check=True,
                capture_output=True
            )
            print("✓ CDK configuration is valid")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ CDK validation failed: {e}")
            return False

    def _plan_cdk(self) -> bool:
        """Generate CDK diff."""
        try:
            subprocess.run(
                ["cdk", "diff"],
                cwd=self.cdk_dir,
                check=True,
                env={**os.environ, "CDK_ENV": self.config.environment.value}
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ CDK diff failed: {e}")
            return False

    def _deploy_cdk(self) -> bool:
        """Deploy CDK stack."""
        try:
            cmd = ["cdk", "deploy", "--require-approval", "never"]
            subprocess.run(
                cmd,
                cwd=self.cdk_dir,
                check=True,
                env={**os.environ, "CDK_ENV": self.config.environment.value}
            )
            print("✓ CDK deploy completed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ CDK deploy failed: {e}")
            return False

    def _destroy_cdk(self) -> bool:
        """Destroy CDK stack."""
        try:
            subprocess.run(
                ["cdk", "destroy", "--force"],
                cwd=self.cdk_dir,
                check=True,
                env={**os.environ, "CDK_ENV": self.config.environment.value}
            )
            print("✓ CDK destroy completed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ CDK destroy failed: {e}")
            return False

    def _output_cdk(self) -> dict:
        """Get CDK outputs."""
        # CDK outputs are shown during deploy
        return {}

    # Pulumi operations
    def _validate_pulumi(self) -> bool:
        """Validate Pulumi configuration."""
        try:
            subprocess.run(
                ["pulumi", "preview", "--non-interactive"],
                cwd=self.pulumi_dir,
                check=True,
                capture_output=True
            )
            print("✓ Pulumi configuration is valid")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Pulumi validation failed: {e}")
            return False

    def _plan_pulumi(self) -> bool:
        """Generate Pulumi preview."""
        try:
            subprocess.run(
                ["pulumi", "preview", "--stack", self.config.environment.value],
                cwd=self.pulumi_dir,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Pulumi preview failed: {e}")
            return False

    def _deploy_pulumi(self) -> bool:
        """Deploy Pulumi stack."""
        try:
            subprocess.run(
                ["pulumi", "up", "--yes", "--stack", self.config.environment.value],
                cwd=self.pulumi_dir,
                check=True
            )
            print("✓ Pulumi up completed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Pulumi up failed: {e}")
            return False

    def _destroy_pulumi(self) -> bool:
        """Destroy Pulumi stack."""
        try:
            subprocess.run(
                ["pulumi", "destroy", "--yes", "--stack", self.config.environment.value],
                cwd=self.pulumi_dir,
                check=True
            )
            print("✓ Pulumi destroy completed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Pulumi destroy failed: {e}")
            return False

    def _output_pulumi(self) -> dict:
        """Get Pulumi outputs."""
        try:
            result = subprocess.run(
                ["pulumi", "stack", "output", "--json", "--stack", self.config.environment.value],
                cwd=self.pulumi_dir,
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError:
            return {}


def run_security_scan(project_root: Path) -> bool:
    """Run security scans on infrastructure code."""
    terraform_dir = project_root / "terraform"

    print("Running security scans...")

    # Run tfsec
    try:
        subprocess.run(
            ["tfsec", str(terraform_dir), "--format", "lovely"],
            check=True
        )
        print("✓ tfsec scan passed")
    except FileNotFoundError:
        print("⚠ tfsec not installed, skipping")
    except subprocess.CalledProcessError:
        print("✗ tfsec found issues")
        return False

    # Run checkov
    try:
        subprocess.run(
            ["checkov", "-d", str(terraform_dir), "--quiet", "--compact"],
            check=True
        )
        print("✓ checkov scan passed")
    except FileNotFoundError:
        print("⚠ checkov not installed, skipping")
    except subprocess.CalledProcessError:
        print("✗ checkov found issues")
        return False

    return True


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="AWS Infrastructure Automation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s validate --tool terraform
  %(prog)s plan --tool terraform --env dev
  %(prog)s deploy --tool terraform --env staging
  %(prog)s output --tool terraform
  %(prog)s cost-estimate
  %(prog)s security-scan
        """
    )

    parser.add_argument(
        "action",
        choices=["validate", "plan", "deploy", "destroy", "output", "cost-estimate", "security-scan"],
        help="Action to perform"
    )
    parser.add_argument(
        "--tool", "-t",
        choices=["terraform", "cdk", "pulumi"],
        default="terraform",
        help="IaC tool to use (default: terraform)"
    )
    parser.add_argument(
        "--env", "-e",
        choices=["dev", "staging", "production"],
        default="dev",
        help="Target environment (default: dev)"
    )
    parser.add_argument(
        "--region", "-r",
        default="us-west-2",
        help="AWS region (default: us-west-2)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Skip confirmation prompts"
    )

    args = parser.parse_args()

    # Determine project root
    project_root = Path(__file__).parent.parent.resolve()

    # Handle actions that don't need full config
    if args.action == "security-scan":
        success = run_security_scan(project_root)
        sys.exit(0 if success else 1)

    # Create configuration
    config = InfraConfig(
        tool=IaCTool(args.tool),
        environment=Environment(args.env),
        region=args.region,
        project_root=project_root,
        dry_run=args.dry_run,
        auto_approve=args.auto_approve
    )

    # Create manager and execute action
    manager = InfrastructureManager(config)

    actions = {
        "validate": manager.validate,
        "plan": manager.plan,
        "deploy": manager.deploy,
        "destroy": manager.destroy,
        "output": lambda: print(json.dumps(manager.output(), indent=2)),
        "cost-estimate": lambda: print(json.dumps(manager.cost_estimate(), indent=2))
    }

    success = actions[args.action]()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
