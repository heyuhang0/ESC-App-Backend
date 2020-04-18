import requests
from flask import current_app


def send_emails(recipients, subject, text):
    requests.post(
        current_app.config['MAILGUN_API_URL'],
        auth=("api", current_app.config['MAILGUN_API_KEY']),
        data={
            "from": current_app.config['MAILGUN_SENDER'],
            "to": recipients,
            "subject": subject,
            "text": text
        })
