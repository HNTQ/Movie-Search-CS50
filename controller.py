from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
import helpers as h

db = SQL("sqlite:///application.db")


def form_test(inputs):
    message = ""
    for element in inputs:
        print(element, inputs[element])
        # Ensure element was submitted
        if not inputs[element]:
            message = "Must provide " + element
            break
    return message


def login_db_test(email, password):
    message = ""
    # Query database for email
    rows = db.execute("SELECT * FROM user WHERE email = ?", email.lower())

    # Ensure username exists and password is correct
    if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
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


def password_requirement(password, confirm_password=""):
    message = ""
    if confirm_password:
        if confirm_password != password:
            message = "Passwords do not match"
    if not h.match_requirements(password, 10):
        message = "Password do not match the minimum requirements"

    return message
