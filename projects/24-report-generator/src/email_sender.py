"""Email delivery for portfolio reports."""
from __future__ import annotations

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailSender:
    """Send portfolio reports via email."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize email sender.

        Args:
            config: Email configuration dictionary with keys:
                - smtp_server: SMTP server hostname
                - smtp_port: SMTP port (default: 587)
                - smtp_user: SMTP username
                - smtp_password: SMTP password
                - from_address: Sender email address
                - from_name: Sender name (optional)
                - use_tls: Whether to use TLS (default: True)
        """
        self.config = config
        self.smtp_server = config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = config.get('smtp_port', 587)
        self.smtp_user = config.get('smtp_user')
        self.smtp_password = config.get('smtp_password')
        self.from_address = config.get('from_address', self.smtp_user)
        self.from_name = config.get('from_name', 'Portfolio Report Generator')
        self.use_tls = config.get('use_tls', True)

        if not self.smtp_user or not self.smtp_password:
            raise ValueError("SMTP credentials not configured")

        logger.info(f"Email sender initialized: {self.smtp_server}:{self.smtp_port}")

    def _create_message(
        self,
        to_addresses: List[str],
        subject: str,
        body_html: str,
        body_text: Optional[str] = None
    ) -> MIMEMultipart:
        """
        Create email message.

        Args:
            to_addresses: List of recipient email addresses
            subject: Email subject
            body_html: HTML email body
            body_text: Plain text email body (optional)

        Returns:
            MIMEMultipart message
        """
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{self.from_name} <{self.from_address}>"
        msg['To'] = ', '.join(to_addresses)
        msg['Subject'] = subject
        msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')

        # Add text part (fallback)
        if body_text:
            text_part = MIMEText(body_text, 'plain')
            msg.attach(text_part)

        # Add HTML part
        html_part = MIMEText(body_html, 'html')
        msg.attach(html_part)

        return msg

    def _attach_file(self, msg: MIMEMultipart, file_path: Path):
        """
        Attach file to email message.

        Args:
            msg: Email message
            file_path: Path to file to attach
        """
        try:
            with open(file_path, 'rb') as f:
                attachment = MIMEBase('application', 'octet-stream')
                attachment.set_payload(f.read())
                encoders.encode_base64(attachment)
                attachment.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{file_path.name}"'
                )
                msg.attach(attachment)
                logger.debug(f"Attached file: {file_path.name}")
        except Exception as e:
            logger.error(f"Error attaching file {file_path}: {e}")

    def _send_message(self, msg: MIMEMultipart, to_addresses: List[str]):
        """
        Send email message via SMTP.

        Args:
            msg: Email message
            to_addresses: List of recipient addresses
        """
        try:
            logger.info(f"Connecting to SMTP server: {self.smtp_server}:{self.smtp_port}")

            # Connect to SMTP server
            if self.use_tls:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)

            # Login
            server.login(self.smtp_user, self.smtp_password)
            logger.debug("SMTP login successful")

            # Send email
            server.send_message(msg)
            logger.info(f"Email sent successfully to: {', '.join(to_addresses)}")

            # Disconnect
            server.quit()

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed. Check credentials.")
            raise
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            raise

    def send_weekly_report(
        self,
        report_paths: List[Path],
        recipients: List[str]
    ):
        """
        Send weekly portfolio report.

        Args:
            report_paths: List of report file paths
            recipients: List of recipient email addresses
        """
        logger.info("Preparing weekly report email...")

        # Email subject
        week_num = datetime.now().strftime('%U')
        subject = f"Weekly Portfolio Report - Week {week_num} ({datetime.now().strftime('%Y-%m-%d')})"

        # Email body
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .summary {{ background: #f5f5f5; padding: 15px; border-left: 4px solid #4CAF50; margin: 20px 0; }}
                .footer {{ background: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
                ul {{ list-style-type: none; padding: 0; }}
                li {{ padding: 5px 0; }}
                li:before {{ content: "✓ "; color: #4CAF50; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Weekly Portfolio Report</h1>
                <p>Week {week_num} - {datetime.now().strftime('%B %d, %Y')}</p>
            </div>

            <div class="content">
                <p>Hello,</p>

                <p>Your weekly portfolio report is ready. This report includes:</p>

                <div class="summary">
                    <ul>
                        <li>Current project statuses and completion percentages</li>
                        <li>Code metrics and statistics</li>
                        <li>Technology stack breakdown</li>
                        <li>Quality indicators (tests, CI/CD, documentation)</li>
                    </ul>
                </div>

                <p>The report is attached in both HTML and PDF formats for your convenience.</p>

                <p><strong>Attachments:</strong></p>
                <ul>
                    {''.join([f'<li>{path.name}</li>' for path in report_paths])}
                </ul>

                <p>To view the HTML report, save the attachment and open it in your web browser.</p>

                <p>Best regards,<br>
                Portfolio Report Generator</p>
            </div>

            <div class="footer">
                <p>This is an automated report generated by the Portfolio Report Generator.</p>
                <p>Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
        </body>
        </html>
        """

        text_body = f"""
Weekly Portfolio Report - Week {week_num}

Your weekly portfolio report is ready.

This report includes:
- Current project statuses and completion percentages
- Code metrics and statistics
- Technology stack breakdown
- Quality indicators

Attachments:
{''.join([f'- {path.name}' for path in report_paths])}

Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

---
This is an automated report.
        """

        # Create message
        msg = self._create_message(recipients, subject, html_body, text_body)

        # Attach reports
        for report_path in report_paths:
            if report_path.exists():
                self._attach_file(msg, report_path)

        # Send email
        self._send_message(msg, recipients)

    def send_monthly_summary(
        self,
        report_paths: List[Path],
        recipients: List[str]
    ):
        """
        Send monthly executive summary.

        Args:
            report_paths: List of report file paths
            recipients: List of recipient email addresses
        """
        logger.info("Preparing monthly summary email...")

        # Email subject
        month = datetime.now().strftime('%B %Y')
        subject = f"Monthly Portfolio Executive Summary - {month}"

        # Email body
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: #2196F3; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .highlight {{ background: #e3f2fd; padding: 15px; border-left: 4px solid #2196F3; margin: 20px 0; }}
                .footer {{ background: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
                ul {{ list-style-type: disc; padding-left: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📈 Monthly Portfolio Executive Summary</h1>
                <p>{month}</p>
            </div>

            <div class="content">
                <p>Dear Stakeholder,</p>

                <p>Please find attached the comprehensive monthly portfolio summary for {month}.</p>

                <div class="highlight">
                    <h3>This month's reports include:</h3>
                    <ul>
                        <li><strong>Executive Summary</strong> - High-level overview and key metrics</li>
                        <li><strong>Project Status Report</strong> - Detailed status of all projects</li>
                        <li><strong>Technical Documentation</strong> - Architecture and implementation details</li>
                    </ul>
                </div>

                <p><strong>Report Formats:</strong></p>
                <p>All reports are provided in both HTML and PDF formats. Choose the format that best suits your needs:</p>
                <ul>
                    <li>PDF - Ideal for printing and archiving</li>
                    <li>HTML - Interactive viewing with full formatting</li>
                </ul>

                <p><strong>Attached Files ({len(report_paths)}):</strong></p>
                <ul>
                    {''.join([f'<li>{path.name} ({path.stat().st_size // 1024} KB)</li>' if path.exists() else f'<li>{path.name}</li>' for path in report_paths])}
                </ul>

                <p>If you have any questions or need additional information, please don't hesitate to reach out.</p>

                <p>Best regards,<br>
                Portfolio Management Team</p>
            </div>

            <div class="footer">
                <p>Automated Monthly Report | Portfolio Report Generator</p>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
        </body>
        </html>
        """

        text_body = f"""
Monthly Portfolio Executive Summary - {month}

Dear Stakeholder,

Please find attached the comprehensive monthly portfolio summary.

This month's reports include:
- Executive Summary
- Project Status Report
- Technical Documentation

All reports are provided in both HTML and PDF formats.

Attached files:
{''.join([f'- {path.name}' for path in report_paths])}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

---
Automated Monthly Report
        """

        # Create message
        msg = self._create_message(recipients, subject, html_body, text_body)

        # Attach reports
        for report_path in report_paths:
            if report_path.exists():
                self._attach_file(msg, report_path)

        # Send email
        self._send_message(msg, recipients)

    def send_custom_report(
        self,
        report_paths: List[Path],
        recipients: List[str],
        subject: str,
        message: str
    ):
        """
        Send custom report email.

        Args:
            report_paths: List of report file paths
            recipients: List of recipient email addresses
            subject: Email subject
            message: Email message body
        """
        logger.info("Preparing custom report email...")

        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: #673AB7; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ background: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Portfolio Report</h1>
            </div>

            <div class="content">
                <p>{message}</p>

                <p><strong>Attached Reports:</strong></p>
                <ul>
                    {''.join([f'<li>{path.name}</li>' for path in report_paths])}
                </ul>
            </div>

            <div class="footer">
                <p>Portfolio Report Generator</p>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
        </body>
        </html>
        """

        # Create message
        msg = self._create_message(recipients, subject, html_body, message)

        # Attach reports
        for report_path in report_paths:
            if report_path.exists():
                self._attach_file(msg, report_path)

        # Send email
        self._send_message(msg, recipients)


def main():
    """Test email sender functionality."""
    import argparse

    parser = argparse.ArgumentParser(description='Test email sender')
    parser.add_argument('--smtp-server', required=True, help='SMTP server')
    parser.add_argument('--smtp-port', type=int, default=587, help='SMTP port')
    parser.add_argument('--smtp-user', required=True, help='SMTP username')
    parser.add_argument('--smtp-password', required=True, help='SMTP password')
    parser.add_argument('--from-address', help='From email address')
    parser.add_argument('--to', required=True, nargs='+', help='Recipient(s)')
    parser.add_argument('--reports', nargs='+', help='Report files to attach')

    args = parser.parse_args()

    config = {
        'smtp_server': args.smtp_server,
        'smtp_port': args.smtp_port,
        'smtp_user': args.smtp_user,
        'smtp_password': args.smtp_password,
        'from_address': args.from_address or args.smtp_user,
        'from_name': 'Portfolio Report Generator (Test)'
    }

    sender = EmailSender(config)

    report_paths = [Path(r) for r in args.reports] if args.reports else []

    sender.send_weekly_report(report_paths, args.to)
    logger.info("Test email sent successfully!")


if __name__ == '__main__':
    main()
