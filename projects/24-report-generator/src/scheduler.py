"""Scheduled report generation using APScheduler."""
from __future__ import annotations

import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

import yaml
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from generate_report import ReportGenerator
from email_sender import EmailSender

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScheduledReportGenerator:
    """Manages scheduled report generation and delivery."""

    def __init__(
        self,
        portfolio_root: Path,
        templates_dir: Path,
        output_dir: Path,
        config: Optional[Dict[str, Any]] = None,
        background: bool = False
    ):
        """
        Initialize scheduled report generator.

        Args:
            portfolio_root: Root directory of portfolio
            templates_dir: Directory containing templates
            output_dir: Directory for generated reports
            config: Configuration dictionary
            background: Use background scheduler (default: blocking)
        """
        self.portfolio_root = portfolio_root
        self.templates_dir = templates_dir
        self.output_dir = output_dir
        self.config = config or {}

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize generator
        self.generator = ReportGenerator(
            portfolio_root,
            templates_dir,
            config
        )

        # Initialize email sender if configured
        self.email_sender = None
        if self.config.get('email', {}).get('enabled'):
            self.email_sender = EmailSender(self.config['email'])

        # Initialize scheduler
        if background:
            self.scheduler = BackgroundScheduler()
        else:
            self.scheduler = BlockingScheduler()

        logger.info("Scheduled report generator initialized")

    def generate_and_send_weekly_report(self):
        """Generate and send weekly portfolio report."""
        logger.info("Starting weekly report generation...")

        try:
            # Generate reports
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            weekly_dir = self.output_dir / f"weekly_{timestamp}"
            weekly_dir.mkdir(parents=True, exist_ok=True)

            # Generate HTML and PDF
            reports_generated = []

            for format in ['html', 'pdf']:
                output_file = weekly_dir / f"weekly-report.{format}"
                try:
                    self.generator.render_template(
                        'weekly.html',
                        output_file,
                        format=format
                    )
                    reports_generated.append(output_file)
                    logger.info(f"Generated {format.upper()} report: {output_file}")
                except Exception as e:
                    logger.error(f"Error generating {format} report: {e}")

            # Send via email if configured
            if self.email_sender and reports_generated:
                recipients = self.config.get('email', {}).get('weekly_recipients', [])
                if recipients:
                    self.email_sender.send_weekly_report(
                        reports_generated,
                        recipients
                    )
                    logger.info(f"Weekly report sent to {len(recipients)} recipient(s)")

            logger.info("Weekly report generation completed")

        except Exception as e:
            logger.error(f"Error in weekly report generation: {e}", exc_info=True)

    def generate_and_send_monthly_summary(self):
        """Generate and send monthly executive summary."""
        logger.info("Starting monthly summary generation...")

        try:
            # Generate reports
            timestamp = datetime.now().strftime('%Y%m')
            monthly_dir = self.output_dir / f"monthly_{timestamp}"
            monthly_dir.mkdir(parents=True, exist_ok=True)

            # Generate multiple report types
            templates = [
                ('executive_summary.html', 'executive-summary'),
                ('project_status.html', 'project-status'),
                ('technical_documentation.html', 'technical-docs')
            ]

            reports_generated = []

            for template, basename in templates:
                for format in ['html', 'pdf']:
                    output_file = monthly_dir / f"{basename}.{format}"
                    try:
                        self.generator.render_template(
                            template,
                            output_file,
                            format=format
                        )
                        reports_generated.append(output_file)
                        logger.info(f"Generated {basename}.{format}")
                    except Exception as e:
                        logger.error(f"Error generating {basename}.{format}: {e}")

            # Send via email if configured
            if self.email_sender and reports_generated:
                recipients = self.config.get('email', {}).get('monthly_recipients', [])
                if recipients:
                    self.email_sender.send_monthly_summary(
                        reports_generated,
                        recipients
                    )
                    logger.info(f"Monthly summary sent to {len(recipients)} recipient(s)")

            logger.info("Monthly summary generation completed")

        except Exception as e:
            logger.error(f"Error in monthly summary generation: {e}", exc_info=True)

    def generate_daily_stats(self):
        """Generate daily statistics report."""
        logger.info("Generating daily statistics...")

        try:
            timestamp = datetime.now().strftime('%Y%m%d')
            daily_dir = self.output_dir / "daily" / timestamp
            daily_dir.mkdir(parents=True, exist_ok=True)

            # Generate quick status HTML
            output_file = daily_dir / "daily-stats.html"
            self.generator.render_template(
                'project_status.html',
                output_file,
                format='html'
            )

            logger.info(f"Daily statistics generated: {output_file}")

        except Exception as e:
            logger.error(f"Error generating daily stats: {e}", exc_info=True)

    def setup_schedules(self):
        """Set up all scheduled jobs."""
        schedules = self.config.get('schedules', {})

        # Weekly report (default: Monday 9 AM)
        weekly_schedule = schedules.get('weekly', {
            'day_of_week': 'mon',
            'hour': 9,
            'minute': 0
        })
        self.scheduler.add_job(
            self.generate_and_send_weekly_report,
            trigger=CronTrigger(**weekly_schedule),
            id='weekly_report',
            name='Weekly Portfolio Report'
        )
        logger.info(f"Scheduled weekly report: {weekly_schedule}")

        # Monthly summary (default: 1st of month, 9 AM)
        monthly_schedule = schedules.get('monthly', {
            'day': 1,
            'hour': 9,
            'minute': 0
        })
        self.scheduler.add_job(
            self.generate_and_send_monthly_summary,
            trigger=CronTrigger(**monthly_schedule),
            id='monthly_summary',
            name='Monthly Executive Summary'
        )
        logger.info(f"Scheduled monthly summary: {monthly_schedule}")

        # Daily stats (default: every day 8 AM)
        daily_schedule = schedules.get('daily', {
            'hour': 8,
            'minute': 0
        })
        self.scheduler.add_job(
            self.generate_daily_stats,
            trigger=CronTrigger(**daily_schedule),
            id='daily_stats',
            name='Daily Statistics'
        )
        logger.info(f"Scheduled daily stats: {daily_schedule}")

        # Optional: Test job (every 5 minutes)
        if schedules.get('test_mode', False):
            self.scheduler.add_job(
                self.generate_daily_stats,
                trigger=IntervalTrigger(minutes=5),
                id='test_job',
                name='Test Job (5 min interval)'
            )
            logger.info("Test job scheduled (every 5 minutes)")

    def start(self):
        """Start the scheduler."""
        self.setup_schedules()

        logger.info("Starting scheduler...")
        logger.info("Active jobs:")
        for job in self.scheduler.get_jobs():
            logger.info(f"  - {job.name} (ID: {job.id})")
            logger.info(f"    Next run: {job.next_run_time}")

        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped")

    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logger.info("Scheduler shutdown")


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}")
        return {}

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def main():
    """CLI entry point for scheduled report generator."""
    parser = argparse.ArgumentParser(
        description='Scheduled Portfolio Report Generator'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/scheduler.yml',
        help='Configuration file path'
    )
    parser.add_argument(
        '--portfolio-root',
        type=str,
        help='Portfolio root directory'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./reports',
        help='Output directory for reports'
    )
    parser.add_argument(
        '--test-mode',
        action='store_true',
        help='Run in test mode (5 min intervals)'
    )
    parser.add_argument(
        '--run-once',
        choices=['weekly', 'monthly', 'daily'],
        help='Run a job once and exit'
    )

    args = parser.parse_args()

    # Determine paths
    if args.portfolio_root:
        portfolio_path = Path(args.portfolio_root)
    else:
        portfolio_path = Path(__file__).parent.parent.parent.parent

    templates_dir = Path(__file__).parent.parent / "templates"
    output_dir = Path(args.output_dir)

    # Load config
    config_path = Path(args.config)
    config = load_config(config_path)

    # Override test mode
    if args.test_mode:
        if 'schedules' not in config:
            config['schedules'] = {}
        config['schedules']['test_mode'] = True

    # Initialize generator
    generator = ScheduledReportGenerator(
        portfolio_path,
        templates_dir,
        output_dir,
        config,
        background=False
    )

    # Run once if requested
    if args.run_once:
        logger.info(f"Running {args.run_once} job once...")
        if args.run_once == 'weekly':
            generator.generate_and_send_weekly_report()
        elif args.run_once == 'monthly':
            generator.generate_and_send_monthly_summary()
        elif args.run_once == 'daily':
            generator.generate_daily_stats()
        logger.info("Job completed. Exiting.")
        return

    # Start scheduler
    generator.start()


if __name__ == '__main__':
    main()
