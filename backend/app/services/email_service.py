"""
Email service — sends transactional emails via SMTP (Gmail / SendGrid / any SMTP).

Security notes:
- Never logs email body or OTP codes
- Uses TLS (STARTTLS on port 587 or SSL on port 465)
- Connection errors are caught and re-raised as clean exceptions
"""

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.core.config import settings

logger = logging.getLogger(__name__)


def _build_otp_html(otp_code: str, purpose: str, expires_minutes: int = 3) -> str:
    action = "verify your email and complete registration" if purpose == "register" else "reset your password"
    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="margin:0;padding:0;background:#0f0f0f;font-family:system-ui,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f0f0f;padding:40px 20px;">
        <tr>
          <td align="center">
            <table width="480" cellpadding="0" cellspacing="0"
                   style="background:#1a1a1a;border:1px solid #2a2a2a;border-radius:16px;overflow:hidden;">
              <!-- Header -->
              <tr>
                <td style="background:#f59e0b;padding:24px 32px;text-align:center;">
                  <span style="font-size:28px;">📚</span>
                  <h1 style="margin:8px 0 0;color:#0f0f0f;font-size:20px;font-weight:700;">
                    Parkash Book Depot
                  </h1>
                </td>
              </tr>
              <!-- Body -->
              <tr>
                <td style="padding:32px;">
                  <p style="color:#e5e5e5;font-size:16px;margin:0 0 8px;">
                    Use the code below to {action}:
                  </p>
                  <!-- OTP Box -->
                  <div style="background:#0f0f0f;border:2px solid #f59e0b;border-radius:12px;
                              padding:28px;text-align:center;margin:24px 0;">
                    <span style="font-size:48px;font-weight:800;letter-spacing:16px;
                                 color:#f59e0b;font-family:monospace;">
                      {otp_code}
                    </span>
                  </div>
                  <p style="color:#a3a3a3;font-size:14px;margin:0;">
                    ⏱ This code expires in <strong style="color:#e5e5e5;">{expires_minutes} minutes</strong>.
                  </p>
                  <p style="color:#a3a3a3;font-size:14px;margin:12px 0 0;">
                    🔒 Never share this code with anyone. Parkash Book Depot staff will
                    <strong style="color:#e5e5e5;">never</strong> ask for it.
                  </p>
                  <p style="color:#a3a3a3;font-size:14px;margin:12px 0 0;">
                    If you didn't request this, you can safely ignore this email.
                  </p>
                </td>
              </tr>
              <!-- Footer -->
              <tr>
                <td style="border-top:1px solid #2a2a2a;padding:16px 32px;text-align:center;">
                  <p style="color:#525252;font-size:12px;margin:0;">
                    © Parkash Book Depot · This is an automated message, do not reply.
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


async def send_otp_email(to_email: str, otp_code: str, purpose: str) -> None:
    """
    Send OTP email. Raises RuntimeError on SMTP failure.
    otp_code is passed in — we log nothing about it here.
    """
    subject = (
        "Verify your email — Parkash Book Depot"
        if purpose == "register"
        else "Reset your password — Parkash Book Depot"
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Parkash Book Depot <{settings.SMTP_FROM}>"
    msg["To"] = to_email

    html_body = _build_otp_html(otp_code, purpose)
    msg.attach(MIMEText(html_body, "html"))

    try:
        if settings.SMTP_PORT == 465:
            # SSL
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_FROM, to_email, msg.as_string())
        else:
            # STARTTLS (587 or 25)
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_FROM, to_email, msg.as_string())

        logger.info(f"OTP email sent to {to_email} [purpose={purpose}]")

    except smtplib.SMTPException as e:
        logger.error(f"SMTP error sending to {to_email}: {type(e).__name__}")
        raise RuntimeError("Failed to send verification email. Please try again.") from e