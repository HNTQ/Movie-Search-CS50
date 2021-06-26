import os
import random
import re
import smtplib
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from functools import wraps
from flask import session, render_template, redirect


def getCode(length):
    # generate random string with length size"""
    code = string.ascii_lowercase
    return ''.join(random.choice(code) for i in range(length))


def activationMail(email, username, code):
    msg = MIMEMultipart()
    msg['From'] = 'moviesearch@noreply.npak0382.odns.fr'
    msg['To'] = email
    msg['Subject'] = 'movieSearch Account activation'
    message = """ Hello """ + username + """ 
    
Please confirm your account using the following code: """ + code + """

You can use this link to activate your account http://127.0.0.1:5000/activate?email=""" + email + """&code=""" + code + """
    
Best regards, 
    
Movie-Search Team
    """
    msg.attach(MIMEText(message))
    mailServer = smtplib.SMTP_SSL('kapre.o2switch.net', 465)
    mailServer.login('moviesearch@noreply.npak0382.odns.fr', os.environ.get('EMAIL_PASSWORD'))
    mailServer.sendmail('moviesearch@noreply.npak0382.odns.fr', email, msg.as_string())
    mailServer.quit()
    return True


# Check if user is logged in
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


# Check if the password match minimum requirements
# Here one capital letter, one number and one special character
def match_requirements(password, min_size=0):
    if not password:
        return False
    if re.search("[A-Z]", password) and re.search("[0-9]", password) and re.search("[!@#$%^&*(),.?:{}|<>+-]", password) and re.search("[a-z]", password):
        if len(password) >= min_size:
            return True
    return False

  
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
