from flask import Flask
from flask_mail import Mail, Message

class Email():
    def send_email(self, receivers, title, content, header):
        mail = Mail()
        with mail.connect() as conn:
            for receiver in receivers:
                msg = Message(receiver, content, title)
                conn.send(msg)
        print("Mail sent")
    