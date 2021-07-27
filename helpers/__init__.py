from flask import session, render_template, redirect, request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps
from os import getenv
import smtplib
import random
import string
import re


# ///////////////////////////
#  1 - GENERAL
# ///////////////////////////


# Check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


# To be reviewed
def handle_error(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("errors.html", message=message), code


def get_missing_input(inputs):
    for input in inputs:
        # Ensure element was submitted
        if not inputs[input]:
            return f"Must provide {input}"



# ///////////////////////////
#  2 - AUTH
# ///////////////////////////


def send_activation_mail(email, username, code):
    msg = MIMEMultipart()
    msg['From'] = 'moviesearch@noreply.npak0382.odns.fr'
    msg['To'] = email
    msg['Subject'] = 'movieSearch Account activation'
    message = """ Hello """ + username + """ 
    
Please confirm your account using the following code: """ + code + """

You can use this link to activate your account """+request.host_url+"""activate?email=""" + email +\
              """&code=""" + code + """
              
    
Best regards, 
    
Movie-Search Team
    """
    msg.attach(MIMEText(message))
    mailServer = smtplib.SMTP_SSL(getenv('SERVEUR_URL'), 465)
    mailServer.login(getenv('EMAIL_ID'), getenv('EMAIL_PASSWORD'))
    mailServer.sendmail(getenv('EMAIL_ID'), email, msg.as_string())
    mailServer.quit()

    return True


# Generate a random string with length size
def generate_code(length):
    code = string.ascii_lowercase
    return ''.join(random.choice(code) for i in range(length))


# Check if the password match minimum requirements
# Here one capital letter, one number and one special character
def match_requirements(password, min_size=0):
    if not password:
        return False
    if re.search("[A-Z]", password) and re.search("[0-9]", password) and\
            re.search("[!@#$%^&*(),.?:{}|<>+-]", password) and re.search("[a-z]", password):
        if len(password) >= min_size:
            return True
    return False



def password_requirement(password, confirm_password=""):
    if confirm_password and confirm_password != password:
        return "Passwords do not match"
    if not match_requirements(password, 10):
        return "Password do not match the minimum requirements"