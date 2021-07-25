from flask import Blueprint, render_template, request, session
import controller as c
import helpers as h

user_bp = Blueprint('user_bp', __name__, template_folder="../templates", static_folder='../static')

@user_bp.route("/profile", methods=["GET", "POST"])
@h.login_required
def profile():
    return render_template("profile.html")


@user_bp.route("/parameters", methods=["GET", "POST"])
@h.login_required
def parameters():
    email = c.get_email(session["user_id"])
    if request.method == "POST":
        if request.form.get("change_email"):
            new_email = request.form.get("email")
            password = request.form.get("pass")
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
            return render_template("parameters.html", email=new_email, email_message=success_message)

        elif request.form.get("change_password"):
            current_password = request.form.get("current")
            new_password = request.form.get("password")
            confirm_password = request.form.get("confirmation")

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