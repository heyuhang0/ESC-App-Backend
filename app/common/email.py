from flask_mail importMail, Message

class Email(public):
    def send_email(receivers, title, content, header):
        msg = Message(header, receivers)
        msg.body = content
        mail.send(msg)
        print("Mail sent")
    