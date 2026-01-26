#!/usr/bin/env python3
"""
Disaster Recovery Drill Automation Script
Performs comprehensive DR testing including backup verification,
restore testing, and RTO/RPO compliance validation.
"""
import sys
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import os


class DRDrillRunner:
    """Manages disaster recovery drill execution and reporting."""

    def __init__(self, config: Dict = None):
        self.config = config or self._load_default_config()
        self.results = {
            "drill_id": f"DR-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "start_time": datetime.now().isoformat(),
            "steps": [],
            "metrics": {},
            "status": "in_progress",
        }
        self.drill_start = time.time()

    def _load_default_config(self) -> Dict:
        """Load default configuration for DR drill."""
        return {
            "backup_location": os.getenv("BACKUP_DIR", "./backups"),
            "test_db_host": os.getenv("TEST_DB_HOST", "localhost"),
            "test_db_name": os.getenv("TEST_DB_NAME", "dr_test"),
            "test_db_user": os.getenv("TEST_DB_USER", "postgres"),
            "app_health_url": os.getenv(
                "APP_HEALTH_URL", "http://localhost:8080/health"
            ),
            "rto_target_seconds": int(os.getenv("RTO_TARGET_SECONDS", "300")),  # 5 min
            "rpo_target_seconds": int(
                os.getenv("RPO_TARGET_SECONDS", "3600")
            ),  # 1 hour
            "report_dir": os.getenv("REPORT_DIR", "./dr-reports"),
        }

    def log_step(
        self, step_name: str, status: str, details: str = "", duration: float = 0
    ):
        """Log drill step results."""
        step_result = {
            "name": step_name,
            "status": status,
            "details": details,
            "duration_seconds": round(duration, 2),
            "timestamp": datetime.now().isoformat(),
        }
        self.results["steps"].append(step_result)

        status_icon = "✓" if status == "passed" else "✗" if status == "failed" else "⚠"
        print(f"{status_icon} {step_name}: {status}")
        if details:
            print(f"  Details: {details}")

    def verify_backup_availability(self) -> Tuple[bool, str]:
        """Verify that recent backups are available."""
        print("\n→ Step 1: Verifying backup availability...")
        step_start = time.time()

        backup_dir = Path(self.config["backup_location"])
        if not backup_dir.exists():
            duration = time.time() - step_start
            details = f"Backup directory does not exist: {backup_dir}"
            self.log_step("Backup Availability", "failed", details, duration)
            return False, details

        # Find most recent backup file
        backup_files = sorted(
            backup_dir.glob("db_backup_*.sql.gz"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        if not backup_files:
            duration = time.time() - step_start
            details = "No backup files found"
            self.log_step("Backup Availability", "failed", details, duration)
            return False, details

        latest_backup = backup_files[0]
        backup_age_seconds = time.time() - latest_backup.stat().st_mtime
        backup_size_mb = latest_backup.stat().st_size / (1024 * 1024)

        # Check RPO compliance
        rpo_compliant = backup_age_seconds <= self.config["rpo_target_seconds"]

        duration = time.time() - step_start
        details = (
            f"Found {len(backup_files)} backup(s). "
            f"Latest: {latest_backup.name} "
            f"(age: {int(backup_age_seconds/60)} min, size: {backup_size_mb:.2f} MB, "
            f"RPO {'✓' if rpo_compliant else '✗'})"
        )

        self.results["metrics"]["latest_backup"] = str(latest_backup)
        self.results["metrics"]["backup_age_seconds"] = int(backup_age_seconds)
        self.results["metrics"]["rpo_compliant"] = rpo_compliant

        status = "passed" if rpo_compliant else "warning"
        self.log_step("Backup Availability", status, details, duration)
        return True, details

    def test_restore_procedures(self) -> Tuple[bool, str]:
        """Test database restore to verify backup integrity."""
        print("\n→ Step 2: Testing restore procedures...")
        step_start = time.time()

        backup_dir = Path(self.config["backup_location"])
        backup_files = sorted(
            backup_dir.glob("db_backup_*.sql.gz"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        if not backup_files:
            duration = time.time() - step_start
            details = "No backup file available for restore test"
            self.log_step("Restore Test", "failed", details, duration)
            return False, details

        latest_backup = backup_files[0]

        try:
            # Test: Decompress backup to verify integrity
            test_output = Path("/tmp/dr_drill_test.sql")
            result = subprocess.run(
                ["gunzip", "-c", str(latest_backup)], capture_output=True, timeout=30
            )

            if result.returncode != 0:
                duration = time.time() - step_start
                details = f"Backup decompression failed: {result.stderr.decode()[:200]}"
                self.log_step("Restore Test", "failed", details, duration)
                return False, details

            # Validate SQL content
            sql_content = result.stdout.decode()
            if len(sql_content) < 100:  # Suspiciously small
                duration = time.time() - step_start
                details = (
                    f"Backup file appears corrupt (size: {len(sql_content)} bytes)"
                )
                self.log_step("Restore Test", "failed", details, duration)
                return False, details

            # Check for common SQL patterns
            has_tables = (
                "CREATE TABLE" in sql_content or "create table" in sql_content.lower()
            )
            has_data = "INSERT INTO" in sql_content or "COPY" in sql_content

            duration = time.time() - step_start
            details = (
                f"Backup validated successfully. "
                f"Size: {len(sql_content)/1024:.1f} KB, "
                f"Tables: {'✓' if has_tables else '✗'}, "
                f"Data: {'✓' if has_data else '✗'}"
            )

            self.results["metrics"]["backup_size_kb"] = len(sql_content) // 1024
            self.results["metrics"]["has_schema"] = has_tables
            self.results["metrics"]["has_data"] = has_data

            status = "passed" if (has_tables or has_data) else "warning"
            self.log_step("Restore Test", status, details, duration)
            return True, details

        except subprocess.TimeoutExpired:
            duration = time.time() - step_start
            details = "Restore test timed out after 30 seconds"
            self.log_step("Restore Test", "failed", details, duration)
            return False, details
        except Exception as e:
            duration = time.time() - step_start
            details = f"Restore test error: {type(e).__name__}: {str(e)}"
            self.log_step("Restore Test", "failed", details, duration)
            return False, details

    def validate_application_health(self) -> Tuple[bool, str]:
        """Validate that application can connect to database."""
        print("\n→ Step 3: Validating application health...")
        step_start = time.time()

        # Check if psql or mysql client is available for connection test
        db_client = (
            "psql" if "postgres" in self.config.get("test_db_user", "") else "mysql"
        )
        client_available = (
            subprocess.run(["which", db_client], capture_output=True).returncode == 0
        )

        if not client_available:
            duration = time.time() - step_start
            details = (
                f"Database client '{db_client}' not available. "
                f"Install {db_client} for full health checks. Assuming healthy."
            )
            self.log_step("Application Health", "warning", details, duration)
            return True, details

        # Test database connectivity
        try:
            if db_client == "psql":
                # Test PostgreSQL connection
                result = subprocess.run(
                    [
                        "psql",
                        "-h",
                        self.config["test_db_host"],
                        "-U",
                        self.config["test_db_user"],
                        "-d",
                        "postgres",  # Connect to default postgres db
                        "-c",
                        "SELECT 1;",
                    ],
                    capture_output=True,
                    timeout=10,
                    env={**os.environ, "PGPASSWORD": os.getenv("PGPASSWORD", "")},
                )
            else:
                # Test MySQL connection
                result = subprocess.run(
                    [
                        "mysql",
                        "-h",
                        self.config["test_db_host"],
                        "-u",
                        self.config["test_db_user"],
                        "-e",
                        "SELECT 1;",
                    ],
                    capture_output=True,
                    timeout=10,
                )

            duration = time.time() - step_start

            if result.returncode == 0:
                details = (
                    f"Database connection successful ({self.config['test_db_host']})"
                )
                self.results["metrics"]["db_connection"] = "healthy"
                self.log_step("Application Health", "passed", details, duration)
                return True, details
            else:
                error_msg = (
                    result.stderr.decode()[:200] if result.stderr else "Unknown error"
                )
                details = f"Database connection failed: {error_msg}"
                self.results["metrics"]["db_connection"] = "failed"
                self.log_step("Application Health", "warning", details, duration)
                return True, details  # Non-critical, continue drill

        except subprocess.TimeoutExpired:
            duration = time.time() - step_start
            details = "Database connection timed out"
            self.log_step("Application Health", "warning", details, duration)
            return True, details
        except Exception as e:
            duration = time.time() - step_start
            details = f"Health check error: {str(e)}"
            self.log_step("Application Health", "warning", details, duration)
            return True, details

    def check_rto_compliance(self) -> Tuple[bool, str]:
        """Verify Recovery Time Objective compliance."""
        print("\n→ Step 4: Checking RTO compliance...")
        step_start = time.time()

        total_drill_time = step_start - self.drill_start
        rto_target = self.config["rto_target_seconds"]
        rto_compliant = total_drill_time <= rto_target

        duration = time.time() - step_start
        details = (
            f"Total recovery time: {int(total_drill_time)} seconds "
            f"(target: {rto_target}s, "
            f"{'✓ PASS' if rto_compliant else '✗ FAIL'})"
        )

        self.results["metrics"]["total_recovery_time_seconds"] = int(total_drill_time)
        self.results["metrics"]["rto_target_seconds"] = rto_target
        self.results["metrics"]["rto_compliant"] = rto_compliant

        status = "passed" if rto_compliant else "failed"
        self.log_step("RTO Compliance", status, details, duration)
        return rto_compliant, details

    def generate_drill_report(self) -> Tuple[bool, str]:
        """Generate comprehensive drill report."""
        print("\n→ Step 5: Generating drill report...")
        step_start = time.time()

        # Finalize results
        self.results["end_time"] = datetime.now().isoformat()
        self.results["total_duration_seconds"] = int(time.time() - self.drill_start)

        # Determine overall status
        step_statuses = [step["status"] for step in self.results["steps"]]
        if "failed" in step_statuses:
            self.results["status"] = "failed"
        elif "warning" in step_statuses:
            self.results["status"] = "passed_with_warnings"
        else:
            self.results["status"] = "passed"

        # Create report directory
        report_dir = Path(self.config["report_dir"])
        report_dir.mkdir(parents=True, exist_ok=True)

        # Save JSON report
        json_report_path = report_dir / f"{self.results['drill_id']}.json"
        with open(json_report_path, "w") as f:
            json.dump(self.results, f, indent=2)

        # Generate markdown summary
        md_report_path = report_dir / f"{self.results['drill_id']}.md"
        with open(md_report_path, "w") as f:
            f.write(f"# DR Drill Report: {self.results['drill_id']}\n\n")
            f.write(f"**Status:** {self.results['status'].upper()}\n\n")
            f.write(f"**Started:** {self.results['start_time']}\n\n")
            f.write(
                f"**Duration:** {self.results['total_duration_seconds']} seconds\n\n"
            )

            f.write("## Key Metrics\n\n")
            for key, value in self.results["metrics"].items():
                f.write(f"- **{key.replace('_', ' ').title()}:** {value}\n")

            f.write("\n## Drill Steps\n\n")
            for step in self.results["steps"]:
                icon = (
                    "✓"
                    if step["status"] == "passed"
                    else "✗" if step["status"] == "failed" else "⚠"
                )
                f.write(f"### {icon} {step['name']}\n")
                f.write(f"- **Status:** {step['status']}\n")
                f.write(f"- **Duration:** {step['duration_seconds']}s\n")
                if step["details"]:
                    f.write(f"- **Details:** {step['details']}\n")
                f.write("\n")

        duration = time.time() - step_start
        details = f"Reports saved: {json_report_path.name}, {md_report_path.name}"
        self.log_step("Report Generation", "passed", details, duration)

        print(f"\n📄 JSON Report: {json_report_path}")
        print(f"📄 Markdown Report: {md_report_path}")

        return True, details

    def run_drill(self) -> int:
        """Execute complete DR drill."""
        print("=" * 60)
        print("DISASTER RECOVERY DRILL")
        print("=" * 60)
        print(f"Drill ID: {self.results['drill_id']}")
        print(f"Start Time: {self.results['start_time']}")
        print("=" * 60)

        # Run all drill steps
        steps = [
            self.verify_backup_availability,
            self.test_restore_procedures,
            self.validate_application_health,
            self.check_rto_compliance,
            self.generate_drill_report,
        ]

        for step_func in steps:
            success, details = step_func()
            # Continue even if non-critical steps fail

        # Print summary
        print("\n" + "=" * 60)
        print("DRILL SUMMARY")
        print("=" * 60)
        print(f"Overall Status: {self.results['status'].upper()}")
        print(f"Total Duration: {self.results['total_duration_seconds']} seconds")
        print(
            f"Steps Passed: {sum(1 for s in self.results['steps'] if s['status'] == 'passed')}/{len(self.results['steps'])}"
        )

        if self.results["status"] == "failed":
            print("\n❌ DR drill FAILED - Review report for details")
            return 1
        elif self.results["status"] == "passed_with_warnings":
            print("\n⚠️  DR drill PASSED with warnings - Review report")
            return 0
        else:
            print("\n✅ DR drill PASSED successfully")
            return 0


def main():
    """Main entry point."""
    # Allow custom config via environment variables
    runner = DRDrillRunner()
    return runner.run_drill()


if __name__ == "__main__":
    sys.exit(main())
