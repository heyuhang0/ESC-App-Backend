import requests
import json
from typing import List
from flask import current_app
from app.models import User


def send_emails(users: List[User], subject: str, html: str):
    recipient_addresses = []
    recipient_variables = {}
    for user in users:
        recipient_addresses.append(user.email)
        recipient_variables[user.email] = {
            'id': user.id,
            'name': user.full_name,
            'email': user.email
        }

    response = requests.post(
        current_app.config['MAILGUN_API_URL'],
        auth=('api', current_app.config['MAILGUN_API_KEY']),
        data={
            'from': current_app.config['MAILGUN_SENDER'],
            'to': recipient_addresses,
            'recipient-variables': json.dumps(recipient_variables),
            'subject': subject,
            'html': html
        })

    if response.status_code != 200:
        raise Exception('Error when send email: {}'.format(response.json()))
