import logging
import resend

from app.core.config import settings

logger = logging.getLogger(__name__)

resend.api_key = settings.RESEND_API_KEY


def _build_otp_html(
    otp_code: str,
    purpose: str,
    expires_minutes: int = 3
) -> str:
    action = (
        "verify your email and complete registration"
        if purpose == "register"
        else "reset your password"
    )

    return f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2>📚 Parkash Book Depot</h2>

        <p>
            Use the code below to {action}
        </p>

        <div style="
            font-size:40px;
            font-weight:bold;
            letter-spacing:8px;
            padding:20px;
            border:2px solid #f59e0b;
            display:inline-block;
        ">
            {otp_code}
        </div>

        <p>
            This code expires in {expires_minutes} minutes.
        </p>

        <p>
            Never share this code with anyone.
        </p>
    </body>
    </html>
    """


async def send_otp_email(
    to_email: str,
    otp_code: str,
    purpose: str
) -> None:

    subject = (
        "Verify your email — Parkash Book Depot"
        if purpose == "register"
        else "Reset your password — Parkash Book Depot"
    )

    try:
        resend.Emails.send(
            {
                "from": settings.EMAIL_FROM,
                "to": [to_email],
                "subject": subject,
                "html": _build_otp_html(
                    otp_code,
                    purpose
                ),
            }
        )

        logger.info(
            f"OTP email sent to {to_email} [purpose={purpose}]"
        )

    except Exception as e:
        logger.error(
            f"Resend error sending email: {str(e)}"
        )

        raise RuntimeError(
            "Failed to send verification email. Please try again."
        ) from e
    