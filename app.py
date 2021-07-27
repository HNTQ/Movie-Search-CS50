from flask import Flask, redirect, render_template, request, session, url_for
from cs50 import SQL
from flask_session import Session
from tempfile import mkdtemp
from os import getenv
from dotenv import load_dotenv
import helpers as h

load_dotenv()

app = Flask(__name__)

print(getenv("DATABASE_URL"))

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

from routes.auth.auth import auth_bp
from routes.general.general import general_bp
from routes.user.user import user_bp
from routes.search.search import search_bp

app.register_blueprint(auth_bp)
app.register_blueprint(general_bp)
app.register_blueprint(user_bp)
app.register_blueprint(search_bp)

if __name__ == '__main__':
    app.run()
