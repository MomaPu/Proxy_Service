from celery import Celery
from ..core.config import settings
import smtplib
from email.message import EmailMessage

celery_app = Celery(
    "tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)


@celery_app.task
def send_activation_email(email: str, activation_key: str):
    """Отправка письма с ключом активации"""
    msg = EmailMessage()
    msg["Subject"] = "Ваш ключ активации"
    msg["From"] = settings.MAIL_FROM
    msg["To"] = email
    msg.set_content(f"""
    Здравствуйте!

    Ваш ключ активации: {activation_key}

    Для подключения к прокси-серверу используйте этот ключ в десктопном приложении.

    Ключ действителен в течение 24 часов.

    С уважением,
    Proxy Service
    """)

    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.send_message(msg)
        return {"status": "sent", "email": email}
    except Exception as e:
        return {"status": "error", "error": str(e)}