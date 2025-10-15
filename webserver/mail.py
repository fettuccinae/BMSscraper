import re
import smtplib
import ssl
from email.message import EmailMessage
import os

SERVER_USERNAME = os.environ.get("SERVER_USERNAME")
SERVER_PASSWORD = os.environ.get("SERVER_PASSWORD")

def send_mail(subject, body, user_email):
    with smtplib.SMTP(host="in-v3.mailjet.com", port=587) as mailer:
        mailer.starttls(context=ssl.create_default_context())
        mailer.login(SERVER_USERNAME, SERVER_PASSWORD)

        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = "periodic_notifs@outlook.com"
        msg["To"] = user_email

        mailer.send_message(msg)


def cron_job_mail_sending(data):
    for d in data:
        try:
            name = re.search(
                r"(.*\/((vijayawada\/)|(hyderabad\/)))([^\/]+)(\/.*)", d["scrape_url"]
            ).group(5)

        except Exception as error:
            print(d["scrape_url"] + error)
            continue

        subject = f"Update for {name}"
        body = (
            str(d["detail"])
            + "\n Server has now stopped tracking this event. If you want to keep tracking this event, please go on website and add it again. (Too lazy to think what to do for this condition)"
        )
        send_mail(subject, body, d["mail_id"])
