from flask import Blueprint, render_template, request, session, redirect, url_for
from helpers import get_missing_input, password_requirement, login_required
from models import User
import i18n


user_bp = Blueprint(
    "user_bp", __name__, template_folder="../../templates", static_folder="../../static"
)


@user_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    return render_template("profile.html")


@user_bp.route("/parameters", methods=["GET", "POST"])
@login_required
def parameters():
    email = User.get_email(session["user_id"])
    if request.method == "POST":
        if request.form.get("change_email"):
            new_email = request.form.get("email")
            password = request.form.get("pass")
            inputs = {"email": new_email, "password": password}

            # Ensure form submitted is fully completed
            missing_input = get_missing_input(inputs)
            if missing_input:
                return render_template(
                    "parameters.html",
                    email=email,
                    email_message=i18n.t("missing_input", input=missing_input),
                )

            # Query database for email
            query = User.check_credentials(email, password)
            message = query["message"]
            if message:
                return render_template(
                    "parameters.html", email=email, email_message=message
                )

            # Ensure email is not already used
            if not User.email_exist(new_email):
                return render_template(
                    "parameters.html", email=email, email_message="Error"
                )

            User.update_email(new_email, session["user_id"])
            return render_template(
                "parameters.html", email=new_email, email_message="Success"
            )

        elif request.form.get("change_password"):
            current_password = request.form.get("current")
            new_password = request.form.get("password")
            confirm_password = request.form.get("confirmation")

            inputs = {
                "old password": current_password,
                "new password": new_password,
                "confirmation": confirm_password,
            }

            # Ensure form submitted is fully completed
            missing_input = get_missing_input(inputs)
            if missing_input:
                return render_template(
                    "parameters.html",
                    email=email,
                    password_message=i18n.t("missing_input", input=missing_input),
                )

            query = User.check_credentials(email, current_password)
            message = query["message"]
            if message:
                return render_template(
                    "parameters.html", email=email, password_message=message
                )

            # Ensure passwords respect minimum requirement and match
            password_message = password_requirement(new_password, confirm_password)
            if password_message:
                return render_template(
                    "parameters.html", email=email, password_message=password_message
                )

            User.update_password(new_password, session["user_id"])

            success_message = "Password Updated"
            return render_template(
                "parameters.html", email=email, password_message=success_message
            )

        elif request.form.get("delete_account"):
            # ensure delete function work correctly
            if User.delete_account(session["user_id"]):
                session.clear()
                return redirect(
                    url_for("auth_bp.login", message=i18n.t("account_deleted"))
                )
            return render_template(
                "parameters.html",
                email=email,
                delete_message=i18n.t("account_deleted_error"),
            )

    else:
        return render_template("parameters.html", email=email)
