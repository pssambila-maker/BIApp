"""Email service for sending reports via SMTP."""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Optional, Dict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.email_config import EmailConfiguration
from app.utils.encryption import get_encryption_service


class EmailService:
    """Service for sending emails via SMTP."""

    def __init__(self):
        self.encryption = get_encryption_service()

    async def get_user_email_config(
        self,
        user_id: UUID,
        db: AsyncSession
    ) -> Optional[EmailConfiguration]:
        """
        Get user's email configuration.

        Args:
            user_id: User ID
            db: Database session

        Returns:
            EmailConfiguration or None if not configured
        """
        result = await db.execute(
            select(EmailConfiguration).where(EmailConfiguration.owner_id == user_id)
        )
        return result.scalar_one_or_none()

    async def test_connection(
        self,
        user_id: UUID,
        db: AsyncSession
    ) -> Dict[str, str]:
        """
        Test SMTP connection with user's configuration.

        Args:
            user_id: User ID
            db: Database session

        Returns:
            Dict with status and message

        Raises:
            ValueError: If email config not found
        """
        config = await self.get_user_email_config(user_id, db)

        if not config:
            raise ValueError("Email configuration not found for user")

        try:
            # Decrypt password
            password = self.encryption.decrypt(config.smtp_password_encrypted)

            # Test connection
            if config.use_ssl:
                server = smtplib.SMTP_SSL(config.smtp_host, config.smtp_port, timeout=10)
            else:
                server = smtplib.SMTP(config.smtp_host, config.smtp_port, timeout=10)
                if config.use_tls:
                    server.starttls()

            server.login(config.smtp_username, password)
            server.quit()

            return {"status": "success", "message": "SMTP connection successful"}

        except smtplib.SMTPAuthenticationError:
            return {"status": "error", "message": "Authentication failed. Check username and password."}
        except smtplib.SMTPException as e:
            return {"status": "error", "message": f"SMTP error: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": f"Connection error: {str(e)}"}

    async def send_report_email(
        self,
        user_id: UUID,
        recipients: List[str],
        subject: str,
        body_html: str,
        attachments: Optional[List[Path]] = None,
        db: AsyncSession = None
    ) -> Dict[str, any]:
        """
        Send report email with attachments.

        Args:
            user_id: User ID (to get SMTP config)
            recipients: List of recipient email addresses
            subject: Email subject
            body_html: HTML email body
            attachments: List of file paths to attach
            db: Database session

        Returns:
            Dict with status, message, and sent_to list

        Raises:
            ValueError: If email config not found or invalid
        """
        if not recipients:
            raise ValueError("No recipients specified")

        # Get user's email configuration
        config = await self.get_user_email_config(user_id, db)

        if not config:
            raise ValueError("Email configuration not found. Please configure SMTP settings first.")

        # Decrypt SMTP password
        try:
            password = self.encryption.decrypt(config.smtp_password_encrypted)
        except Exception as e:
            raise ValueError(f"Failed to decrypt SMTP password: {str(e)}")

        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{config.from_name} <{config.from_email}>" if config.from_name else config.from_email
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject

        # Attach HTML body
        html_part = MIMEText(body_html, 'html')
        msg.attach(html_part)

        # Attach files
        attached_files = []
        if attachments:
            for file_path in attachments:
                if not file_path.exists():
                    print(f"Warning: Attachment not found: {file_path}")
                    continue

                try:
                    with open(file_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())

                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {file_path.name}'
                    )
                    msg.attach(part)
                    attached_files.append(file_path.name)
                except Exception as e:
                    print(f"Warning: Failed to attach {file_path}: {e}")

        # Send email
        try:
            if config.use_ssl:
                server = smtplib.SMTP_SSL(config.smtp_host, config.smtp_port, timeout=30)
            else:
                server = smtplib.SMTP(config.smtp_host, config.smtp_port, timeout=30)
                if config.use_tls:
                    server.starttls()

            server.login(config.smtp_username, password)
            server.send_message(msg)
            server.quit()

            return {
                "status": "success",
                "message": f"Email sent to {len(recipients)} recipient(s)",
                "sent_to": recipients,
                "attachments": attached_files
            }

        except smtplib.SMTPAuthenticationError as e:
            raise ValueError(f"SMTP authentication failed: {str(e)}")
        except smtplib.SMTPException as e:
            raise ValueError(f"SMTP error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to send email: {str(e)}")

    async def send_alert_notification(
        self,
        user_id: UUID,
        recipients: List[str],
        alert_name: str,
        condition_description: str,
        condition_value: any,
        message: Optional[str] = None,
        db: AsyncSession = None
    ) -> Dict[str, any]:
        """
        Send alert notification email.

        Args:
            user_id: User ID
            recipients: List of recipient emails
            alert_name: Name of the alert
            condition_description: Description of the condition that triggered
            condition_value: The value that triggered the alert
            message: Optional custom message
            db: Database session

        Returns:
            Dict with status and sent_to
        """
        subject = f"⚠️ Alert Triggered: {alert_name}"

        # Create HTML body
        body_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    color: #333;
                }}
                .alert-box {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                }}
                .alert-title {{
                    color: #856404;
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .alert-details {{
                    font-size: 14px;
                    margin: 10px 0;
                }}
                .value {{
                    font-weight: bold;
                    color: #d9534f;
                }}
                .footer {{
                    margin-top: 30px;
                    font-size: 11px;
                    color: #999;
                    border-top: 1px solid #ddd;
                    padding-top: 10px;
                }}
            </style>
        </head>
        <body>
            <h2>Alert Notification</h2>

            <div class="alert-box">
                <div class="alert-title">⚠️ {alert_name}</div>
                <div class="alert-details">
                    <strong>Condition:</strong> {condition_description}<br>
                    <strong>Current Value:</strong> <span class="value">{condition_value}</span>
                </div>
                {f'<div class="alert-details"><strong>Message:</strong> {message}</div>' if message else ''}
            </div>

            <div class="footer">
                This is an automated alert from your BI Platform.<br>
                Triggered at: {Path(__file__).stem}
            </div>
        </body>
        </html>
        """

        return await self.send_report_email(
            user_id=user_id,
            recipients=recipients,
            subject=subject,
            body_html=body_html,
            db=db
        )

    @staticmethod
    def get_smtp_presets() -> Dict[str, Dict[str, any]]:
        """
        Get common SMTP provider presets.

        Returns:
            Dict of provider name to configuration
        """
        return {
            "gmail": {
                "smtp_host": "smtp.gmail.com",
                "smtp_port": 587,
                "use_tls": True,
                "use_ssl": False,
                "note": "Use an App Password, not your regular password. Enable 2FA and generate at: https://myaccount.google.com/apppasswords"
            },
            "outlook": {
                "smtp_host": "smtp-mail.outlook.com",
                "smtp_port": 587,
                "use_tls": True,
                "use_ssl": False,
                "note": "Use your Outlook.com or Office 365 credentials"
            },
            "office365": {
                "smtp_host": "smtp.office365.com",
                "smtp_port": 587,
                "use_tls": True,
                "use_ssl": False,
                "note": "Use your Office 365 email and password"
            },
            "yahoo": {
                "smtp_host": "smtp.mail.yahoo.com",
                "smtp_port": 587,
                "use_tls": True,
                "use_ssl": False,
                "note": "Use an App Password. Generate at: https://login.yahoo.com/account/security"
            },
            "custom": {
                "smtp_host": "",
                "smtp_port": 587,
                "use_tls": True,
                "use_ssl": False,
                "note": "Enter your custom SMTP server details"
            }
        }
