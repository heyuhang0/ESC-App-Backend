from email_validator import validate_email


def email(email_input):
    return validate_email(email_input)['email']
