from flask import session, render_template, redirect
from functools import wraps


# ///////////////////////////
#  GENERAL HELPERS
# ///////////////////////////


def login_required(f):
    """Decorates routes and check if user is logged in."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


# To be reviewed
def handle_error(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("errors.html", message=message), code


def get_missing_input(inputs: dict) -> str:
    """Parse all inputs and return the of the first missing one."""
    for input in inputs:
        if not inputs[input]:
            return input
