from flask import Flask, redirect, render_template, request, session, url_for
from cs50 import SQL
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from api import *
from helpers import *


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

        email = request.form.get("email")
        password = request.form.get("password")

        # Ensure username was submitted
        if not email:
            message = "Must provide email"
            return render_template("login.html", message=message)

        # Ensure password was submitted
        if not password:
            message = "Must provide password"
            return render_template("login.html", message=message)

        # Query database for username
        rows = db.execute("SELECT * FROM user WHERE email = ?", email.lower())

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            message = "Invalid username and/or password"
            return render_template("login.html", message=message)

        if not rows[0]["active"]:
            return redirect(url_for("activate", email=email.lower()))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")
        # User reached route via GET (as by clicking a link or via redirect)
    else:
        if request.args.get('message'):
            message = request.args.get('message')
        else:
            message = ""
        return render_template("login.html", message=message)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            message = "Must provide username"
            return render_template("register.html", message=message)

        # Ensure Email was submitted
        if not email:
            message = "Must provide email"
            return render_template("register.html", message=message)

        # Ensure password was submitted
        if not password:
            message = "Must provide password"
            return render_template("register.html", message=message)

        # Ensure password was confirmed
        if not confirm_password:
            message = "Must confirm password"
            return render_template("register.html", message=message)

        if confirm_password != password:
            message = "Passwords do not match"
            return render_template("register.html", message=message)

        if not match_requirements(password, 10):
            message = "Password do not match the minimum requirements"
            return render_template("register.html", message=message)

        if db.execute("SELECT * FROM user WHERE email = ?", email.lower()):
            message = "Email already used"
            return render_template("register.html", message=message)
        hash_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        db.execute("INSERT INTO user (username, email, hash) VALUES(?, ?, ?)", username, email.lower(), hash_password)

        # mailing
        code = get_code(8)
        activation_mail(email, username, code)

        # save activation code
        user_id = db.execute("SELECT id FROM user WHERE email = ?", email.lower())
        db.execute("INSERT INTO activation (user_id, activation_code) VALUES(?, ?)", user_id[0]["id"], code)
        return redirect(url_for("activate", email=email.lower()))
    else:
        return render_template("register.html")


@app.route("/activate", methods=["GET", "POST"])
def activate():
    if request.method == "POST":

        email = request.form.get("email")
        confirm_code = request.form.get("confirm")
        # Ensure Email was submitted
        if not email:
            message = "Must provide email"
            return render_template("activation.html", message=message)

        # Ensure password was submitted
        if not confirm_code:
            message = "Must provide confirmation code"
            return render_template("activation.html", message=message)

        rows = db.execute("SELECT * FROM activation WHERE user_id = "
                          "(SELECT id FROM user WHERE email = ?)", email.lower())

        user = db.execute("SELECT active FROM user WHERE email = ?", email.lower())

        if len(user) == 1 and user[0]["active"] == 1:
            message = "Account already activated"
            return redirect(url_for("login", message=message))
        if len(rows) != 1 or rows[0]["activation_code"] != confirm_code:
            message = "Invalid Email or confirmation code"
            return render_template("activation.html", message=message)
        db.execute("DELETE FROM activation WHERE id =?", rows[0]["id"])
        db.execute("UPDATE user SET active = true WHERE id = ?", rows[0]["user_id"])
        message = "Account activated"
        return redirect(url_for("login", message=message))
    else:
        code = ""
        email = ""
        if request.args.get('email'):
            email = request.args.get('email')

        if request.args.get('code'):
            code = request.args.get('code')

        if code and email:
            rows = db.execute("SELECT * FROM activation WHERE user_id ="
                              " (SELECT id FROM user WHERE email = ?)", email.lower())
            user = db.execute("SELECT active FROM user WHERE email = ?", email.lower())

            if len(user) == 1 and user[0]["active"] == 1:
                message = "Account already activated"
                return redirect(url_for("login", message=message))
            if len(rows) != 1 or rows[0]["activation_code"] != code:
                message = "Invalid Email or confirmation code"
                return render_template("activation.html", message=message)
            db.execute("DELETE FROM activation WHERE id =?", rows[0]["id"])
            db.execute("UPDATE user SET active = true WHERE id = ?", rows[0]["user_id"])
            message = "Account activated"
            return redirect(url_for("login", message=message))
        return render_template("activation.html", email=email, code=code)


@app.route("/logout")
@login_required
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    return render_template("profile.html")


@app.route("/parameters", methods=["GET", "POST"])
@login_required
def parameters():
    return render_template("parameters.html")


@app.route("/search")
def search():
    """Basic search by title, can take category filters"""
    # Assignment and checks
    title = request.args.get('title')
    # filters = get_categories(request.args.get('filters'))

    if not title:
        return render_template("search.html", error="Please submit a valid search")

    # Corresponding Api request
    query = query_data("title", title)
    results = parse_query_by_title(query)

    return render_template("search.html",
                           movies=results["movies"],
                           series=results["series"])


@app.route("/details/<media_type>/<media_id>")
def details(media_type, media_id):
    if not media_id or not media_type:
        return render_template("search.html", error="Please submit a valid search")

    query = query_data("id", media_id, media_type)

    if query is None:
        return render_template("search.html", error="Please submit a valid search")

    results = parse_detail_by_id(query, media_type)

    return render_template("details.html",
                           media=results["media"],
                           actors=results["actors"],
                           recommendations=results["recommendations"],
                           videos=results["videos"])


if __name__ == '__main__':
    app.run()
