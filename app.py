from flask import Flask, redirect, render_template, request, session
from cs50 import SQL
from flask_session import Session
from tempfile import mkdtemp
app = Flask(__name__)

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

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///application.db")

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html")

@app.route("/userProfil", methods=["GET", "POST"])
def userProfil():
    return render_template("user_profil.html")

@app.route("/parameters", methods=["GET", "POST"])
def parameters():
    return render_template("parameters.html")

@app.route("/results", methods=["GET", "POST"])
def results():
    return render_template("results.html")

@app.route("/details", methods=["GET", "POST"])
def details():
    return render_template("details.html")

if __name__ == '__main__':
    app.run()
