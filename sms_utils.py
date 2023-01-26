import email, smtplib, ssl
from providers import PROVIDERS

def send_sms_via_email(
    number: str,
    message: str,
    provider: str,
    sender_credentials: tuple,
    subject: str = "sent using etext",
    smtp_server: str = "smtp.gmail.com",
    smtp_port: int = 465,
):
    sender_email, email_password = sender_credentials
    receiver_email = f'{number}@{PROVIDERS.get(provider).get("sms")}'

    email_message = f"Subject:{subject}\nTo:{receiver_email}\n{message}"

    with smtplib.SMTP_SSL(
        smtp_server, smtp_port, context=ssl.create_default_context()
    ) as email:
        email.login(sender_email, email_password)
        email.sendmail(sender_email, receiver_email, email_message)
        
def send_sms(message_str:str):
    number = "Your Phone number here (e.g. 1233211234)" #edit this string
    message = message_str
    provider = "your phone provider here(e.g. T-Mobile)" #edit this string
    sender_credentials = ("youremail@gmail.com", "SMTP forwarding password") #edit these two strings
    send_sms_via_email(number, message, provider, sender_credentials)
