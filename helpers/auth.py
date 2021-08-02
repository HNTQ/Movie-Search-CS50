from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import request
from os import getenv
import smtplib
import random
import string
import re


# ///////////////////////////
#  AUTH HELPERS
# ///////////////////////////


def send_activation_mail(email: str, username: str, code: str) -> bool:
    """Send an email to the user in order to activate his account."""

    msg = MIMEMultipart()
    msg["From"] = "moviesearch@noreply.npak0382.odns.fr"
    msg["To"] = email
    msg["Subject"] = "movieSearch Account activation"
    message = (
        """ Hello """
        + username
        + """ 
    
Please confirm your account using the following code: """
        + code
        + """

You can use this link to activate your account """
        + request.host_url
        + """activate?email="""
        + email
        + """&code="""
        + code
        + """
              
    
Best regards, 
    
Movie-Search Team
    """
    )
    msg.attach(MIMEText(message))
    mailServer = smtplib.SMTP_SSL(getenv("SERVEUR_URL"), 465)
    mailServer.login(getenv("EMAIL_ID"), getenv("EMAIL_PASSWORD"))
    mailServer.sendmail(getenv("EMAIL_ID"), email, msg.as_string())
    mailServer.quit()

    return True


# Generate a random string with length size
def generate_code(length: int) -> str:
    code = string.ascii_lowercase
    return "".join(random.choice(code) for i in range(length))


# Check if the password match minimum requirements
# Here one capital letter, one number and one special character
def match_requirements(password: str, min_size: int = 0) -> bool:
    if not password:
        return False
    if (
        re.search("[A-Z]", password)
        and re.search("[0-9]", password)
        and re.search("[!@#$%^&*(),.?:{}|<>+-]", password)
        and re.search("[a-z]", password)
    ):
        if len(password) >= min_size:
            return True
    return False


def password_requirement(password, confirm_password=""):
    if confirm_password and confirm_password != password:
        return "password_wrong_conf"
    if not match_requirements(password, 10):
        return "weak_password"
