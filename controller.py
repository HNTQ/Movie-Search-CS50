from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
import helpers as h

db = SQL("sqlite:///application.db")


def form_test(inputs):
    message = ""
    for element in inputs:
        # Ensure element was submitted
        if not inputs[element]:
            message = "Must provide " + element
            break
    return message


def password_requirement(password, confirm_password=""):
    message = ""
    if confirm_password:
        if confirm_password != password:
            message = "Passwords do not match"
    if not h.match_requirements(password, 10):
        message = "Password do not match the minimum requirements"

    return message


def update_email(email, user_id):
    db.execute("UPDATE user SET email = ? WHERE id = ?", email, user_id)


def update_password(password, user_id):
    hash_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
    db.execute("UPDATE user SET hash = ? WHERE id = ?", hash_password, user_id)


def login_db_test(email, password):
    message = ""
    # Query database for email
    rows = db.execute("SELECT * FROM user WHERE email = ?", email.lower())

    # Ensure username exists and password is correct
    if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
        rows.append("error")
        message = "Invalid username and/or password"

    return {
        "user": rows[0],
        "message": message
    }


def register_db_test(email):
    message = ""
    if db.execute("SELECT * FROM user WHERE email = ?", email.lower()):
        message = "Email already used"

    return message


def register_db_add(password, username, email):
    hash_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
    db.execute("INSERT INTO user (username, email, hash) VALUES(?, ?, ?)", username, email.lower(), hash_password)

    # mailing
    code = h.get_code(8)
    h.activation_mail(email, username, code)

    # save activation code
    user_id = db.execute("SELECT id FROM user WHERE email = ?", email.lower())
    db.execute("INSERT INTO activation (user_id, activation_code) VALUES(?, ?)", user_id[0]["id"], code)


def activation(email, code):
    message = ""
    rows = db.execute("SELECT * FROM activation WHERE user_id ="
                      " (SELECT id FROM user WHERE email = ?)", email.lower())
    user = db.execute("SELECT active FROM user WHERE email = ?", email.lower())

    if len(user) == 1 and user[0]["active"] == 1:
        message = "Account already activated"
    if len(rows) != 1 or rows[0]["activation_code"] != code and not message:
        message = "Invalid Email or confirmation code"
    if not message:
        db.execute("DELETE FROM activation WHERE id =?", rows[0]["id"])
        db.execute("UPDATE user SET active = true WHERE id = ?", rows[0]["user_id"])
    return message


def get_email(user_id):
    query = db.execute("SELECT email FROM user WHERE id = ?", user_id)
    return query[0]["email"]
