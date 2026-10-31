from email.message import EmailMessage
from email.utils import formatdate, make_msgid
import aiosmtplib
import logging
from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

class EmailService:
    @staticmethod
    async def send_welcome_email(
        recipient: str,
        subject: str,
        user_name: str,
        message_body: str = "Your account has been successfully created on our platform."
    ) -> None:
        try:
            message = EmailMessage()
            message["From"] = f"Sports App <{settings.EMAIL_FROM}>"
            message["To"] = recipient
            message["Subject"] = subject
            message["Date"] = formatdate(localtime=True)
            message["Message-ID"] = make_msgid(domain="teamrabbil.com")
            
            body_text = f"Hello {user_name},\n\n{message_body}\n\nBest regards,\nSports App Team"
            message.set_content(body_text)

            use_ssl = (settings.SMTP_PORT == 465)
            use_starttls = (settings.SMTP_PORT == 587)

            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER or None,
                password=settings.SMTP_PASSWORD or None,
                use_tls=use_ssl,
                start_tls=use_starttls
            )
            logger.info(f"--> [Success] Email sent to {recipient}")
        except Exception as exc:
            logger.error(f"--> [Error] Failed to send email to {recipient}: {str(exc)}")
