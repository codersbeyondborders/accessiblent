# email_service.py
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

from dotenv import load_dotenv

load_dotenv()

# Configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "noreply@accessify.com")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Accessify")
EMAIL_MODE = os.getenv("EMAIL_MODE", "mock")  # "smtp" or "mock"
BASE_URL = os.getenv("BASE_URL", "http://localhost:5173")

logger = logging.getLogger(__name__)


def _get_verification_email_html(token: str, full_name: str) -> str:
    """
    Generate HTML template for verification email.
    """
    verification_url = f"{BASE_URL}/verify-email/{token}"
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verify Your Email</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td align="center" style="padding: 40px 0;">
                <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 40px 20px 40px; text-align: center;">
                            <h1 style="margin: 0; color: #333333; font-size: 28px;">Welcome to Accessify!</h1>
                        </td>
                    </tr>
                    
                    <!-- Body -->
                    <tr>
                        <td style="padding: 20px 40px;">
                            <p style="margin: 0 0 20px 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                Hi {full_name},
                            </p>
                            <p style="margin: 0 0 20px 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                Thank you for signing up! Please verify your email address to activate your account and start using Accessify.
                            </p>
                            <p style="margin: 0 0 30px 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                Click the button below to verify your email:
                            </p>
                            
                            <!-- Button -->
                            <table role="presentation" style="margin: 0 auto;">
                                <tr>
                                    <td style="border-radius: 4px; background-color: #4F46E5;">
                                        <a href="{verification_url}" target="_blank" style="display: inline-block; padding: 16px 36px; font-size: 16px; color: #ffffff; text-decoration: none; border-radius: 4px;">
                                            Verify Email Address
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="margin: 30px 0 20px 0; color: #666666; font-size: 14px; line-height: 1.6;">
                                Or copy and paste this link into your browser:
                            </p>
                            <p style="margin: 0 0 20px 0; color: #4F46E5; font-size: 14px; word-break: break-all;">
                                {verification_url}
                            </p>
                            <p style="margin: 20px 0 0 0; color: #999999; font-size: 14px; line-height: 1.6;">
                                This verification link will expire in 7 days.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 40px; background-color: #f8f8f8; border-radius: 0 0 8px 8px;">
                            <p style="margin: 0; color: #999999; font-size: 12px; line-height: 1.6; text-align: center;">
                                If you didn't create an account with Accessify, you can safely ignore this email.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""


def _get_verification_email_text(token: str, full_name: str) -> str:
    """
    Generate plain text template for verification email.
    """
    verification_url = f"{BASE_URL}/verify-email/{token}"
    
    return f"""
Welcome to Accessify!

Hi {full_name},

Thank you for signing up! Please verify your email address to activate your account and start using Accessify.

Verify your email by clicking this link:
{verification_url}

This verification link will expire in 7 days.

If you didn't create an account with Accessify, you can safely ignore this email.

---
Accessify Team
"""


def _get_welcome_email_html(full_name: str, organization_name: str) -> str:
    """
    Generate HTML template for welcome email.
    """
    dashboard_url = f"{BASE_URL}/dashboard"
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to Accessify</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td align="center" style="padding: 40px 0;">
                <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 40px 20px 40px; text-align: center;">
                            <h1 style="margin: 0; color: #333333; font-size: 28px;">🎉 Your Account is Active!</h1>
                        </td>
                    </tr>
                    
                    <!-- Body -->
                    <tr>
                        <td style="padding: 20px 40px;">
                            <p style="margin: 0 0 20px 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                Hi {full_name},
                            </p>
                            <p style="margin: 0 0 20px 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                Welcome to Accessify! Your email has been verified and your account for <strong>{organization_name}</strong> is now active.
                            </p>
                            
                            <h2 style="margin: 30px 0 15px 0; color: #333333; font-size: 20px;">Getting Started</h2>
                            <ol style="margin: 0 0 20px 0; padding-left: 20px; color: #666666; font-size: 16px; line-height: 1.8;">
                                <li><strong>Verify your domain</strong> - Add and verify ownership of your organization's domain</li>
                                <li><strong>Accept the ethics agreement</strong> - Review and accept our responsible use guidelines</li>
                                <li><strong>Register your website</strong> - Add your website's entry URL for remediation</li>
                                <li><strong>Start remediation</strong> - Generate accessible HTML versions of your pages</li>
                            </ol>
                            
                            <!-- Button -->
                            <table role="presentation" style="margin: 30px auto;">
                                <tr>
                                    <td style="border-radius: 4px; background-color: #4F46E5;">
                                        <a href="{dashboard_url}" target="_blank" style="display: inline-block; padding: 16px 36px; font-size: 16px; color: #ffffff; text-decoration: none; border-radius: 4px;">
                                            Go to Dashboard
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="margin: 30px 0 0 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                If you have any questions, feel free to reach out to our support team.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 40px; background-color: #f8f8f8; border-radius: 0 0 8px 8px;">
                            <p style="margin: 0; color: #999999; font-size: 12px; line-height: 1.6; text-align: center;">
                                © 2024 Accessify. Making the web accessible for everyone.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""


def _get_welcome_email_text(full_name: str, organization_name: str) -> str:
    """
    Generate plain text template for welcome email.
    """
    dashboard_url = f"{BASE_URL}/dashboard"
    
    return f"""
Your Account is Active!

Hi {full_name},

Welcome to Accessify! Your email has been verified and your account for {organization_name} is now active.

Getting Started:
1. Verify your domain - Add and verify ownership of your organization's domain
2. Accept the ethics agreement - Review and accept our responsible use guidelines
3. Register your website - Add your website's entry URL for remediation
4. Start remediation - Generate accessible HTML versions of your pages

Go to your dashboard: {dashboard_url}

If you have any questions, feel free to reach out to our support team.

---
© 2024 Accessify. Making the web accessible for everyone.
"""


async def send_verification_email(email: str, token: str, full_name: str) -> None:
    """
    Send verification email to the user.
    
    Args:
        email: Recipient email address
        token: Verification token
        full_name: User's full name
    """
    subject = "Verify Your Email - Accessify"
    html_content = _get_verification_email_html(token, full_name)
    text_content = _get_verification_email_text(token, full_name)
    
    await _send_email(email, subject, html_content, text_content)


async def send_welcome_email(email: str, full_name: str, organization_name: str) -> None:
    """
    Send welcome email to the user after email verification.
    
    Args:
        email: Recipient email address
        full_name: User's full name
        organization_name: Organization name
    """
    subject = "Welcome to Accessify!"
    html_content = _get_welcome_email_html(full_name, organization_name)
    text_content = _get_welcome_email_text(full_name, organization_name)
    
    await _send_email(email, subject, html_content, text_content)


async def _send_email(
    to_email: str,
    subject: str,
    html_content: str,
    text_content: str
) -> None:
    """
    Internal function to send email via SMTP or mock mode.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML version of email
        text_content: Plain text version of email
    """
    if EMAIL_MODE == "mock":
        # Mock mode - just log the email
        logger.info(f"[MOCK EMAIL] To: {to_email}")
        logger.info(f"[MOCK EMAIL] Subject: {subject}")
        logger.info(f"[MOCK EMAIL] Text Content:\n{text_content}")
        print(f"\n{'='*60}")
        print(f"MOCK EMAIL SENT")
        print(f"{'='*60}")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"\n{text_content}")
        print(f"{'='*60}\n")
        return
    
    # SMTP mode - send actual email
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
        message["To"] = to_email
        
        # Attach both plain text and HTML versions
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")
        message.attach(part1)
        message.attach(part2)
        
        # Send email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            if SMTP_USER and SMTP_PASSWORD:
                server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(message)
        
        logger.info(f"Email sent successfully to {to_email}")
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        raise Exception(f"Failed to send email: {str(e)}")
