from flask import Flask, redirect, render_template, request, session
from cs50 import SQL
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
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
    # Forget any user_id
    session.clear()
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("email"):
            message = "Must provide email"
            return render_template("login.html", message=message)

        # Ensure password was submitted
        if not request.form.get("password"):
            message = "Must provide password"
            return render_template("login.html", message=message)

        # Query database for username
        rows = db.execute("SELECT * FROM user WHERE email = ?", request.form.get("email").lower())

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            message = "Invalid username and/or password"
            return render_template("login.html", message=message)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")
        # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            message = "Must provide username"
            return render_template("register.html", message=message)

        # Ensure Email was submitted
        if not request.form.get("email"):
            message = "Must provide email"
            return render_template("register.html", message=message)

        # Ensure password was submitted
        if not request.form.get("password"):
            message = "Must provide password"
            return render_template("register.html", message=message)

        # Ensure password was confirmed
        if not request.form.get("confirmation"):
            message = "Must confirm password"
            return render_template("register.html", message=message)

        if request.form.get("confirmation") != request.form.get("password"):
            message = "Passwords do not match"
            return render_template("register.html", message=message)

        #if db.execute("SELECT * FROM user WHERE username = ?", request.form.get("username").lower()) != []:
        #    message = "Username already used"
        #    return render_template("register.html", message=message)

        if db.execute("SELECT * FROM user WHERE email = ?", request.form.get("email").lower()) != []:
            message = "Email already used"
            return render_template("register.html", message=message)

        db.execute("INSERT INTO user (username, email, hash) VALUES(?, ?, ?)", request.form.get("username").lower(),
                   request.form.get("email").lower(),
                   generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8))
        return redirect("/login")
    else:
        return render_template("register.html")

@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/profil", methods=["GET", "POST"])
def profil():
    return render_template("profil.html")

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
