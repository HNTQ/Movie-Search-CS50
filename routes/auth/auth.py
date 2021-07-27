from flask import Blueprint, render_template,session, redirect, request, url_for
import models as m
import helpers as h

auth_bp = Blueprint('auth_bp', __name__, template_folder="../../templates", static_folder='../../static')

@auth_bp.route("/login", methods=["GET", "POST"])
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
        missing_input = h.get_missing_input(inputs)
        if missing_input:
            return render_template("login.html", message=missing_input)

        # Query database for email
        query = m.login_db_test(email, password)

        user = query["user"]
        message = query["message"]

        if message:
            return render_template("login.html", message=message)

        if not user["active"]:
            return redirect(url_for("auth_bp.activate", email=email.lower()))
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

@auth_bp.route("/register", methods=["GET", "POST"])
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
        missing_input = h.get_missing_input(inputs)
        if missing_input:
            return render_template("register.html", message=missing_input)

        # Ensure passwords respect minimum requirement and match
        password_message = h.password_requirement(password, confirm_password)
        if password_message:
            return render_template("register.html", message=password_message)

        # Ensure email is not already used
        db_message = m.register_db_test(email)
        if db_message:
            return render_template("register.html", message=db_message)

        # add user in database
        m.register_db_add(password, username, email)

        return redirect(url_for("auth_bp.activate", email=email.lower()))
    else:
        return render_template("register.html")

@auth_bp.route("/activate", methods=["GET", "POST"])
def activate():
    if request.method == "POST":

        email = request.form.get("email")
        confirm_code = request.form.get("confirm")

        inputs = {
            "email": email,
            "code": confirm_code
        }
        # Ensure form submitted is fully completed
        missing_input = h.get_missing_input(inputs)
        if missing_input:
            return render_template("activation.html", message=missing_input)

        activation_message = m.activation(email, confirm_code)
        if activation_message:
            return render_template("activation.html", message=activation_message)

        success_message = "Account activated"
        return redirect(url_for("auth_bp.login", message=success_message))
    else:
        code = ""
        email = ""
        if request.args.get('email'):
            email = request.args.get('email')

        if request.args.get('code'):
            code = request.args.get('code')

        if code and email:
            activation_message = m.activation(email, code)
            if activation_message:
                return render_template("activation.html", message=activation_message)

            success_message = "Account activated"
            return redirect(url_for("auth_bp.login", message=success_message))
        return render_template("activation.html", email=email, code=code)

@auth_bp.route("/logout")
@h.login_required
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
