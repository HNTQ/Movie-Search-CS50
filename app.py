from flask import Flask, redirect, render_template, request, session, url_for
from cs50 import SQL
from flask_session import Session
from tempfile import mkdtemp
import controller as c

import api as api
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

        inputs = {
            "email": email,
            "password": password
        }

        # Ensure form submitted is fully completed
        form_message = c.form_test(inputs)
        if form_message:
            return render_template("login.html", message=form_message)

        # Query database for email
        query = c.login_db_test(email, password)

        user = query["user"]
        message = query["message"]

        if message:
            return render_template("login.html", message=message)

        if not user["active"]:
            return redirect(url_for("activate", email=email.lower()))
        # Remember which user has logged in
        session["user_id"] = user["id"]

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

        inputs = {
            "username": username,
            "email": email,
            "password": password,
            "confirmation": confirm_password
        }

        # Ensure form submitted is fully completed
        form_message = c.form_test(inputs)
        if form_message:
            return render_template("register.html", message=form_message)

        # Ensure passwords respect minimum requirement and match
        password_message = c.password_requirement(password, confirm_password)
        if password_message:
            return render_template("register.html", message=password_message)

        # Ensure email is not already used
        db_message = c.register_db_test(email)
        if db_message:
            return render_template("register.html", message=db_message)

        # add user in database
        c.register_db_add(password, username, email)

        return redirect(url_for("activate", email=email.lower()))
    else:
        return render_template("register.html")


@app.route("/activate", methods=["GET", "POST"])
def activate():
    if request.method == "POST":

        email = request.form.get("email")
        confirm_code = request.form.get("confirm")

        inputs = {
            "email": email,
            "code": confirm_code
        }
        # Ensure form submitted is fully completed
        form_message = c.form_test(inputs)
        if form_message:
            return render_template("activation.html", message=form_message)

        activation_message = c.activation(email, confirm_code)
        if activation_message:
            return render_template("activation.html", message=activation_message)

        success_message = "Account activated"
        return redirect(url_for("login", message=success_message))
    else:
        code = ""
        email = ""
        if request.args.get('email'):
            email = request.args.get('email')

        if request.args.get('code'):
            code = request.args.get('code')

        if code and email:
            activation_message = c.activation(email, code)
            if activation_message:
                return render_template("activation.html", message=activation_message)

            success_message = "Account activated"
            return redirect(url_for("login", message=success_message))
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
            inputs = {
                "email": new_email,
                "password": password
            }

            # Ensure form submitted is fully completed
            form_message = c.form_test(inputs)
            if form_message:
                return render_template("parameters.html", email=email, email_message=form_message)

            # Query database for email
            query = c.login_db_test(email, password)
            message = query["message"]
            if message:
                return render_template("parameters.html", email=email, email_message=message)

            # Ensure email is not already used
            db_message = c.register_db_test(new_email)
            if db_message:
                return render_template("parameters.html", email=email, email_message=db_message)

            c.update_email(new_email, session["user_id"])
            success_message = "Email Updated"
            return render_template("parameters.html", email=email, email_message=success_message)

        elif request.form.get("change_password"):
            current_password = request.form.get("current")
            new_password = request.form.get("new")
            confirm_password = request.form.get("confirm")

            inputs = {
                "old password": current_password,
                "new password": new_password,
                "confirmation": confirm_password
            }

            # Ensure form submitted is fully completed
            form_message = c.form_test(inputs)
            if form_message:
                return render_template("parameters.html", email=email, password_message=form_message)

            # Ensure passwords respect minimum requirement and match
            password_message = c.password_requirement(new_password, confirm_password)
            if password_message:
                return render_template("parameters.html", email=email, password_message=password_message)

            c.update_password(new_password, session["user_id"])

            success_message = "Password Updated"
            return render_template("parameters.html", email=email, password_message=success_message)

    else:
        return render_template("parameters.html", email=email)


@app.route("/search")
def search():
    """Basic search by title, can take category filters"""
    # Assignment and checks
    title = request.args.get("title")
    filters = request.args.get("filter")

    if not title:
        return render_template("search.html", error="Please submit a valid search")

    results = api.global_search(title, filters)

    return render_template("search.html",
                           movies=results["movie"],
                           series=results["tv"],
                           people=results["person"])


@app.route("/details/<media_type>/<media_id>")
def details(media_type, media_id):
    if not media_id or not media_type:
        return render_template("search.html", error="Please submit a valid search")

    query = api.query_by_id(media_id, media_type)

    if query is None:
        return render_template("search.html", error="Please submit a valid search")

    results = api.parse_query_by_id(query, media_type)

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
    query = api.query_by_id(tv_id, media_type, season_number, episode_number)
    get_episodes = api.query_by_id(tv_id, media_type, season_number)
    episodes = api.parse_episodes(get_episodes)
    results = api.parse_query_by_id(query, media_type)

    return render_template("details.html",
                           media=results["media"],
                           actors=results["actors"],
                           videos=results["videos"],
                           episodes=episodes,
                           tv_id=tv_id,
                           season_number=season_number)


if __name__ == '__main__':
    app.run()
