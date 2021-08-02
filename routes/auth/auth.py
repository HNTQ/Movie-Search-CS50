from flask import Blueprint, render_template, session, redirect, request, url_for
from models import User
import helpers as h
import i18n


auth_bp = Blueprint(
    "auth_bp", __name__, template_folder="../../templates", static_folder="../../static"
)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()
    if request.method == "POST":

        # Ensure form submitted is fully completed
        inputs = {
            "email": request.form.get("email"),
            "password": request.form.get("password"),
        }

        missing_input = h.get_missing_input(inputs)
        if missing_input:
            return render_template(
                "login.html", message=i18n.t("missing_input", input=missing_input)
            )

        email, password = inputs["email"], inputs["password"]

        # Check if credentials are correct
        credentials = User.check_credentials(email.lower(), password)
        user, error = credentials["user"], credentials["message"]

        if error:
            return render_template("login.html", message=i18n.t(error))
        if not user.active:
            return redirect(url_for("auth_bp.activate", email=email.lower()))

        # Remember which user has logged in
        session["user_id"] = user.id

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    message = request.args.get("message")
    return render_template("login.html", message=message or None)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        inputs = {
            "username": request.form.get("username"),
            "email": request.form.get("email"),
            "password": request.form.get("password"),
            "confirmation": request.form.get("confirmation"),
        }

        # Ensure form submitted is fully completed
        missing_input = h.get_missing_input(inputs)
        if missing_input:
            return render_template(
                "register.html", message=i18n.t("missing_input", input=missing_input)
            )

        username, email, password, confirmation = (
            inputs["username"],
            inputs["email"],
            inputs["password"],
            inputs["confirmation"],
        )

        # Ensure passwords respect minimum requirement and match
        password_error = h.password_requirement(password, confirmation)
        if password_error:
            return render_template("register.html", message=i18n.t(password_error))

        # Ensure email is not already used
        if User.email_exist(email.lower()):
            return render_template("register.html", message=i18n.t("used_password"))

        # Add user in database
        User.add_new(password, username, email.lower())
        return redirect(url_for("auth_bp.activate", email=email.lower()))

    else:
        return render_template("register.html")


@auth_bp.route("/activate", methods=["GET", "POST"])
def activate():
    if request.method == "POST":

        inputs = {
            "email": request.form.get("email"),
            "code": request.form.get("confirm"),
        }
        # Ensure form submitted is fully completed
        missing_input = h.get_missing_input(inputs)
        if missing_input:
            return render_template(
                "activation.html", message=i18n.t("missing_input", input=missing_input)
            )

        email, code = inputs["email"], inputs["code"]

        activation_error = User.activate(email, code)
        if activation_error:
            return render_template("activation.html", message=i18n.t(activation_error))

        return redirect(url_for("auth_bp.login", message=i18n.t("account_activated")))
    else:
        code = ""
        email = ""
        if request.args.get("email"):
            email = request.args.get("email")

        if request.args.get("code"):
            code = request.args.get("code")

        if code and email:
            activation_error = User.activate(email, code)
            if activation_error:
                return render_template("activation.html", message=activation_error)

            return redirect(
                url_for("auth_bp.login", message=i18n.t("account_activated"))
            )

        return render_template("activation.html", email=email, code=code)


@auth_bp.route("/logout")
@h.login_required
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
