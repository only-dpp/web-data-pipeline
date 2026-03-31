import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import get_bool_env, get_env, get_int_env


logger = logging.getLogger(__name__)

SMTP_HOST = get_env("SMTP_HOST", required=True)
SMTP_PORT = get_int_env("SMTP_PORT", 587, required=True)
SMTP_USERNAME = get_env("SMTP_USERNAME", required=True)
SMTP_PASSWORD = get_env("SMTP_PASSWORD", required=True)
SMTP_USE_TLS = get_bool_env("SMTP_USE_TLS", True)
EMAIL_FROM = get_env("EMAIL_FROM", SMTP_USERNAME, required=True)
SMTP_TIMEOUT_SECONDS = get_int_env("SMTP_TIMEOUT_SECONDS", 15)
SMTP_MAX_RETRIES = get_int_env("SMTP_MAX_RETRIES", 2)


def send_html_email(to_email: str, subject: str, html_content: str) -> None:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = EMAIL_FROM
    message["To"] = to_email

    html_part = MIMEText(html_content, "html", "utf-8")
    message.attach(html_part)

    last_error: Exception | None = None

    for attempt in range(1, SMTP_MAX_RETRIES + 1):
        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT_SECONDS) as server:
                if SMTP_USE_TLS:
                    server.starttls()

                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.sendmail(EMAIL_FROM, [to_email], message.as_string())

            logger.info("Email sent successfully to=%s subject=%s", to_email, subject)
            return
        except (smtplib.SMTPException, OSError) as exc:
            last_error = exc
            logger.warning(
                "Email send attempt %s/%s failed for to=%s",
                attempt,
                SMTP_MAX_RETRIES,
                to_email,
            )

    logger.error("Email delivery failed after retries for to=%s", to_email, exc_info=last_error)
    raise RuntimeError("email delivery failed") from last_error
