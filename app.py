from flask import Flask, redirect, render_template, request, session, url_for
from cs50 import SQL
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

import api as a
import helpers as h


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

        if not h.match_requirements(password, 10):
            message = "Password do not match the minimum requirements"
            return render_template("register.html", message=message)

        if db.execute("SELECT * FROM user WHERE email = ?", email.lower()):
            message = "Email already used"
            return render_template("register.html", message=message)
        hash_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        db.execute("INSERT INTO user (username, email, hash) VALUES(?, ?, ?)", username, email.lower(), hash_password)

        # mailing
        code = h.get_code(8)
        h.activation_mail(email, username, code)

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
@h.login_required
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
@h.login_required
def profile():
    return render_template("profile.html")


@app.route("/parameters", methods=["GET", "POST"])
@h.login_required
def parameters():
    query_mail = db.execute("SELECT email FROM user WHERE id = ?", session["user_id"])
    email = query_mail[0]["email"]
    if request.method == "POST":
        if request.form.get("change_email"):
            new_email = request.form.get("email")
            password = request.form.get("password")

            # Ensure username was submitted
            if not new_email:
                message = "Must provide new email"
                return render_template("parameters.html", email=email, email_message=message)

            # Ensure password was submitted
            if not password:
                message = "Must provide password"
                return render_template("parameters.html", email=email, email_message=message)

            # Query database for password
            rows = db.execute("SELECT * FROM user WHERE id = ?", session["user_id"])

            # Ensure password is correct
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
                message = "invalid password"
                return render_template("parameters.html", email=email, email_message=message)

            db.execute("UPDATE user SET email = ? WHERE id = ?", new_email, session["user_id"])

            message = "Email Updated"
            return render_template("parameters.html", email=email, email_message=message)

        elif request.form.get("change_password"):
            current_password = request.form.get("current")
            new_password = request.form.get("new")
            confirm_password = request.form.get("confirm")

            if not current_password:
                message = "Must provide current password"
                return render_template("parameters.html", email=email, password_message=message)

            if not new_password:
                message = "Must provide new password"
                return render_template("parameters.html", email=email, password_message=message)

            if not confirm_password:
                message = "Must confirm new password"
                return render_template("parameters.html", email=email, password_message=message)

            if new_password != confirm_password:
                message = "Passwords do not match"
                return render_template("parameters.html", email=email, password_message=message)

            if not h.match_requirements(new_password, 10):
                message = "Password do not match the minimum requirements"
                return render_template("register.html", message=message)

            # Query database for password
            rows = db.execute("SELECT * FROM user WHERE id = ?", session["user_id"])

            # Ensure password is correct
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], current_password):
                message = "current password is invalid"
                return render_template("parameters.html", email=email, password_message=message)

            hash_password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8)
            db.execute("UPDATE user SET hash = ? WHERE id = ?", hash_password, session["user_id"])

            message = "Password Updated"
            return render_template("parameters.html", email=email, password_message=message)

    else:
        return render_template("parameters.html", email=email)


@app.route("/search")
def search():
    """Basic search by title, can take category filters"""
    # Assignment and checks
    search_filter = request.args.get("filter")
    title = request.args.get("title")
    
    movies = people = series = None
    if not title:
        return render_template("search.html", error="Please submit a valid search")

    results = {
        "movie": [],
        "tv": [],
        "person": []
    }
    # Corresponding Api request
    if search_filter:
        if "movies" in search_filter:
            query = a.query_by_search(title, "movie")
            results["movie"] = a.parse_query_by_title(query, "movie")["movie"]
        if "series" in search_filter:
            query = a.query_by_search(title, "tv")
            results["tv"] = a.parse_query_by_title(query, "tv")["tv"]
        if "people" in search_filter:
            query = a.query_by_search(title, "person")
            results["person"] = a.parse_query_by_title(query, "person")["person"]
    else:
        for media_type in ["movie", "tv", "person"]:
            query = a.query_by_search(title, media_type)
            results[media_type] = a.parse_query_by_title(query, media_type)[media_type]

    movies = results["movie"]
    series = results["tv"]
    people = results["person"]

    print(people)
    return render_template("search.html",
                           movies=movies,
                           series=series,
                           people=people)


@app.route("/details/<media_type>/<media_id>")
def details(media_type, media_id):
    if not media_id or not media_type:
        return render_template("search.html", error="Please submit a valid search")

    query = a.query_data(media_id, media_type)

    if query is None:
        return render_template("search.html", error="Please submit a valid search")

    results = a.parse_detail_by_id(query, media_type)

    return render_template("details.html",
                           media=results["media"],
                           seasons=results["seasons"],
                           actors=results["actors"],
                           recommendations=results["recommendations"],
                           videos=results["videos"],
                           cast=results["cast"])


@app.route("/details/tv/<tv_id>/season/<season_number>/episode/<episode_number>")
def episode_details(tv_id, season_number, episode_number):
    if not tv_id or not season_number or not episode_number:
        return render_template("search.html", error="Please submit a valid search")
    media_type = "tv"
    query = a.query_data(tv_id, media_type, season_number, episode_number)
    get_episodes = a.query_data(tv_id, media_type, season_number)
    episodes = a.parse_episodes(get_episodes)
    results = a.parse_detail_by_id(query, media_type)

    return render_template("details.html",
                           media=results["media"],
                           actors=results["actors"],
                           videos=results["videos"],
                           episodes=episodes,
                           tv_id=tv_id,
                           season_number=season_number)


if __name__ == '__main__':
    app.run()
