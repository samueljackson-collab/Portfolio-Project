#!/usr/bin/env python3
"""
AWS Infrastructure Automation CLI

A command-line interface for managing AWS infrastructure using Terraform.
Provides commands for planning, applying, validating, and estimating costs.

Usage:
    ./src/main.py plan [--env ENV]
    ./src/main.py apply [--env ENV] [--auto-approve]
    ./src/main.py validate
    ./src/main.py cost [--env ENV]
    ./src/main.py destroy [--env ENV] [--auto-approve]
    ./src/main.py status
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple


# ANSI colors for terminal output
class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    CYAN = "\033[0;36m"
    NC = "\033[0m"  # No Color


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def get_terraform_dir() -> Path:
    """Get the Terraform directory."""
    return get_project_root() / "terraform"


def print_header(title: str) -> None:
    """Print a formatted header."""
    print(f"\n{Colors.GREEN}{'=' * 60}{Colors.NC}")
    print(f"{Colors.GREEN}{title:^60}{Colors.NC}")
    print(f"{Colors.GREEN}{'=' * 60}{Colors.NC}\n")


def print_success(message: str) -> None:
    """Print a success message."""
    print(f"{Colors.GREEN}[OK]{Colors.NC} {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}", file=sys.stderr)


def print_warning(message: str) -> None:
    """Print a warning message."""
    print(f"{Colors.YELLOW}[WARN]{Colors.NC} {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")


def run_command(
    cmd: list,
    cwd: Optional[Path] = None,
    capture_output: bool = False,
    check: bool = True,
) -> Tuple[int, str, str]:
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            check=check,
        )
        return result.returncode, result.stdout or "", result.stderr or ""
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout or "", e.stderr or ""
    except FileNotFoundError:
        return 1, "", f"Command not found: {cmd[0]}"


def check_terraform_installed() -> bool:
    """Check if Terraform is installed."""
    returncode, _, _ = run_command(
        ["terraform", "version"], capture_output=True, check=False
    )
    return returncode == 0


def check_aws_credentials() -> bool:
    """Check if AWS credentials are configured."""
    returncode, _, _ = run_command(
        ["aws", "sts", "get-caller-identity"],
        capture_output=True,
        check=False,
    )
    return returncode == 0


def get_tfvars_file(env: str) -> Path:
    """Get the tfvars file path for an environment."""
    terraform_dir = get_terraform_dir()
    tfvars_file = terraform_dir / f"{env}.tfvars"
    return tfvars_file


def terraform_init(terraform_dir: Path, backend: bool = True) -> int:
    """Initialize Terraform."""
    print_info("Initializing Terraform...")

    cmd = ["terraform", "init"]
    if not backend:
        cmd.append("-backend=false")

    returncode, _, stderr = run_command(cmd, cwd=terraform_dir, check=False)

    if returncode == 0:
        print_success("Terraform initialized successfully")
    else:
        print_error(f"Terraform init failed: {stderr}")

    return returncode


def cmd_plan(args: argparse.Namespace) -> int:
    """Execute terraform plan."""
    print_header(f"Terraform Plan ({args.env})")

    terraform_dir = get_terraform_dir()
    tfvars_file = get_tfvars_file(args.env)

    if not tfvars_file.exists():
        print_error(f"Environment file not found: {tfvars_file}")
        available = [f.stem for f in terraform_dir.glob("*.tfvars")]
        print_info(f"Available environments: {', '.join(available)}")
        return 1

    # Check prerequisites
    if not check_terraform_installed():
        print_error("Terraform is not installed")
        return 1

    # Initialize
    if terraform_init(terraform_dir) != 0:
        return 1

    # Plan
    print_info(f"Running terraform plan with {args.env}.tfvars...")
    cmd = ["terraform", "plan", f"-var-file={tfvars_file}"]

    if args.out:
        cmd.extend(["-out", args.out])
        print_info(f"Plan will be saved to: {args.out}")

    returncode, _, _ = run_command(cmd, cwd=terraform_dir, check=False)

    if returncode == 0:
        print_success("Plan completed successfully")
    else:
        print_error("Plan failed")

    return returncode


def cmd_apply(args: argparse.Namespace) -> int:
    """Execute terraform apply."""
    print_header(f"Terraform Apply ({args.env})")

    terraform_dir = get_terraform_dir()
    tfvars_file = get_tfvars_file(args.env)

    if not tfvars_file.exists():
        print_error(f"Environment file not found: {tfvars_file}")
        return 1

    # Check prerequisites
    if not check_terraform_installed():
        print_error("Terraform is not installed")
        return 1

    if not check_aws_credentials():
        print_warning("AWS credentials may not be configured")

    # Confirm if not auto-approve
    if not args.auto_approve:
        print_warning(f"This will apply changes to the {args.env} environment!")
        response = input(f"{Colors.YELLOW}Continue? (yes/no): {Colors.NC}")
        if response.lower() != "yes":
            print_info("Apply cancelled")
            return 0

    # Initialize
    if terraform_init(terraform_dir) != 0:
        return 1

    # Apply
    print_info(f"Applying infrastructure for {args.env}...")
    cmd = ["terraform", "apply", f"-var-file={tfvars_file}"]

    if args.auto_approve:
        cmd.append("-auto-approve")

    returncode, _, _ = run_command(cmd, cwd=terraform_dir, check=False)

    if returncode == 0:
        print_success("Apply completed successfully")

        # Show outputs
        print_info("Infrastructure outputs:")
        run_command(["terraform", "output"], cwd=terraform_dir, check=False)
    else:
        print_error("Apply failed")

    return returncode


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate Terraform configuration."""
    print_header("Terraform Validate")

    terraform_dir = get_terraform_dir()

    if not check_terraform_installed():
        print_error("Terraform is not installed")
        return 1

    # Initialize without backend
    if terraform_init(terraform_dir, backend=False) != 0:
        return 1

    # Format check
    print_info("Checking Terraform formatting...")
    returncode, stdout, _ = run_command(
        ["terraform", "fmt", "-check", "-recursive"],
        cwd=terraform_dir,
        capture_output=True,
        check=False,
    )

    if returncode == 0:
        print_success("All files are properly formatted")
    else:
        print_warning(f"Files need formatting: {stdout}")

    # Validate
    print_info("Validating Terraform configuration...")
    returncode, _, stderr = run_command(
        ["terraform", "validate"],
        cwd=terraform_dir,
        capture_output=True,
        check=False,
    )

    if returncode == 0:
        print_success("Configuration is valid")
    else:
        print_error(f"Validation failed: {stderr}")

    # Validate modules
    print_info("Validating modules...")
    modules_dir = terraform_dir / "modules"
    if modules_dir.exists():
        for module_dir in modules_dir.iterdir():
            if module_dir.is_dir() and (module_dir / "main.tf").exists():
                # Init module
                run_command(
                    ["terraform", "init", "-backend=false"],
                    cwd=module_dir,
                    capture_output=True,
                    check=False,
                )

                # Validate module
                ret, _, err = run_command(
                    ["terraform", "validate"],
                    cwd=module_dir,
                    capture_output=True,
                    check=False,
                )

                if ret == 0:
                    print_success(f"Module {module_dir.name} is valid")
                else:
                    print_error(f"Module {module_dir.name} failed: {err}")

    return returncode


def cmd_cost(args: argparse.Namespace) -> int:
    """Estimate infrastructure costs."""
    print_header(f"Cost Estimation ({args.env})")

    project_root = get_project_root()
    cost_script = project_root / "terraform" / "scripts" / "cost-estimate.sh"

    if not cost_script.exists():
        print_error(f"Cost estimation script not found: {cost_script}")
        return 1

    # Check if infracost is installed
    returncode, _, _ = run_command(
        ["infracost", "--version"], capture_output=True, check=False
    )
    if returncode != 0:
        print_warning("Infracost is not installed")
        print_info("Install: curl -fsSL https://raw.githubusercontent.com/"
                   "infracost/infracost/master/scripts/install.sh | sh")
        print_info("Then run: infracost auth login")
        return 1

    # Run cost estimation
    print_info(f"Estimating costs for {args.env} environment...")
    cmd = [str(cost_script), args.env]

    if args.compare:
        cmd.append("--compare")

    returncode, _, _ = run_command(cmd, cwd=project_root, check=False)

    return returncode


def cmd_destroy(args: argparse.Namespace) -> int:
    """Destroy infrastructure."""
    print_header(f"Terraform Destroy ({args.env})")

    terraform_dir = get_terraform_dir()
    tfvars_file = get_tfvars_file(args.env)

    if not tfvars_file.exists():
        print_error(f"Environment file not found: {tfvars_file}")
        return 1

    # Confirm if not auto-approve
    if not args.auto_approve:
        print_error(f"WARNING: This will DESTROY all resources in {args.env}!")
        response = input(f"{Colors.RED}Type 'destroy' to confirm: {Colors.NC}")
        if response != "destroy":
            print_info("Destroy cancelled")
            return 0

    # Initialize
    if terraform_init(terraform_dir) != 0:
        return 1

    # Destroy
    print_info(f"Destroying infrastructure for {args.env}...")
    cmd = ["terraform", "destroy", f"-var-file={tfvars_file}"]

    if args.auto_approve:
        cmd.append("-auto-approve")

    returncode, _, _ = run_command(cmd, cwd=terraform_dir, check=False)

    if returncode == 0:
        print_success("Destroy completed successfully")
    else:
        print_error("Destroy failed")

    return returncode


def cmd_status(args: argparse.Namespace) -> int:
    """Show infrastructure status."""
    print_header("Infrastructure Status")

    terraform_dir = get_terraform_dir()

    # Check Terraform installation
    print_info("Checking prerequisites...")
    if check_terraform_installed():
        print_success("Terraform is installed")
        returncode, stdout, _ = run_command(
            ["terraform", "version"],
            capture_output=True,
            check=False,
        )
        print(f"    {stdout.split('\n')[0]}")
    else:
        print_error("Terraform is not installed")

    # Check AWS credentials
    if check_aws_credentials():
        print_success("AWS credentials are configured")
        returncode, stdout, _ = run_command(
            ["aws", "sts", "get-caller-identity", "--output", "json"],
            capture_output=True,
            check=False,
        )
        if returncode == 0:
            identity = json.loads(stdout)
            print(f"    Account: {identity.get('Account', 'N/A')}")
            print(f"    ARN: {identity.get('Arn', 'N/A')}")
    else:
        print_warning("AWS credentials are not configured")

    # List available environments
    print_info("\nAvailable environments:")
    for tfvars in terraform_dir.glob("*.tfvars"):
        print(f"    - {tfvars.stem}")

    # Show terraform state if initialized
    if (terraform_dir / ".terraform").exists():
        print_info("\nTerraform state:")
        returncode, stdout, _ = run_command(
            ["terraform", "state", "list"],
            cwd=terraform_dir,
            capture_output=True,
            check=False,
        )
        if returncode == 0 and stdout:
            resource_count = len(stdout.strip().split("\n"))
            print_success(f"State contains {resource_count} resources")
        else:
            print_warning("No state file found or state is empty")

    # Show modules
    modules_dir = terraform_dir / "modules"
    if modules_dir.exists():
        print_info("\nAvailable modules:")
        for module in sorted(modules_dir.iterdir()):
            if module.is_dir() and (module / "main.tf").exists():
                readme = module / "README.md"
                desc = "No description"
                if readme.exists():
                    with open(readme, encoding="utf-8") as f:
                        for line in f:
                            if line.startswith("# "):
                                desc = line[2:].strip()
                                break
                print(f"    - {module.name}: {desc}")

    return 0


def main() -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="AWS Infrastructure Automation CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s plan --env dev          Plan dev environment
  %(prog)s apply --env staging     Apply staging environment
  %(prog)s validate                Validate all configurations
  %(prog)s cost --env production   Estimate production costs
  %(prog)s status                  Show infrastructure status
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Plan command
    plan_parser = subparsers.add_parser("plan", help="Plan infrastructure changes")
    plan_parser.add_argument(
        "--env", "-e", default="dev", help="Environment (dev, staging, production)"
    )
    plan_parser.add_argument("--out", "-o", help="Save plan to file")

    # Apply command
    apply_parser = subparsers.add_parser("apply", help="Apply infrastructure changes")
    apply_parser.add_argument(
        "--env", "-e", default="dev", help="Environment (dev, staging, production)"
    )
    apply_parser.add_argument(
        "--auto-approve", action="store_true", help="Skip confirmation"
    )

    # Validate command
    subparsers.add_parser("validate", help="Validate Terraform configuration")

    # Cost command
    cost_parser = subparsers.add_parser("cost", help="Estimate infrastructure costs")
    cost_parser.add_argument(
        "--env", "-e", default="dev", help="Environment (dev, staging, production)"
    )
    cost_parser.add_argument(
        "--compare", action="store_true", help="Compare with baseline"
    )

    # Destroy command
    destroy_parser = subparsers.add_parser("destroy", help="Destroy infrastructure")
    destroy_parser.add_argument(
        "--env", "-e", default="dev", help="Environment (dev, staging, production)"
    )
    destroy_parser.add_argument(
        "--auto-approve", action="store_true", help="Skip confirmation"
    )

    # Status command
    subparsers.add_parser("status", help="Show infrastructure status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Execute command
    commands = {
        "plan": cmd_plan,
        "apply": cmd_apply,
        "validate": cmd_validate,
        "cost": cmd_cost,
        "destroy": cmd_destroy,
        "status": cmd_status,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
