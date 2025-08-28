import smtplib
import ssl
from email.message import EmailMessage
from flask import current_app


def send_mail(subject, body, user_email):
    with smtplib.SMTP(host="in-v3.mailjet.com", port=587) as mailer:
        mailer.starttls(context=ssl.create_default_context())
        mailer.login(current_app.config["SERVER_USERNAME"], current_app.config["SERVER_PASSWORD"])

        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = "periodic_notifs@outlook.com"
        msg["To"] = user_email

        mailer.send_message(msg)
