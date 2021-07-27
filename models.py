from werkzeug.security import check_password_hash, generate_password_hash
from helpers import generate_code, send_activation_mail
from sqlalchemy import create_engine, MetaData, Table
from os import getenv
from cs50 import SQL


db = SQL("sqlite:///application.db")

class User:

    table = "user"

    def get(user_id):
        return user_id

    def add_new(password, username, email):
        hash_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        db.execute("INSERT INTO user (username, email, hash) VALUES(?, ?, ?)", username, email.lower(), hash_password)

        # mailing
        code = generate_code(8)
        send_activation_mail(email, username, code)

        # save activation code
        user_id = db.execute("SELECT id FROM user WHERE email = ?", email.lower())
        db.execute("INSERT INTO activation (user_id, activation_code) VALUES(?, ?)", user_id[0]["id"], code)


    def update_email(email, user_id):
        db.execute("UPDATE user SET email = ? WHERE id = ?", email, user_id)

    def update_password(password, user_id):
        hash_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        db.execute("UPDATE user SET hash = ? WHERE id = ?", hash_password, user_id)

    def get_email(user_id):
        query = db.execute("SELECT email FROM user WHERE id = ?", user_id)
        return query[0]["email"]

    def check_credentials(email, password):
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

    def is_single_email(self, email):
        if db.execute("SELECT * FROM user WHERE email = ?", email.lower()):
            return "Email already used"
    
    def activate(email, code):
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


# ///////////////////////////
#  # - HELPERS
# ///////////////////////////

# -----------------------------------------------------------
# Insert line(s) in the selected table
# Usage : insert_record("user",{"username": "John","email": "john@email.com"})

# @table_name String,
# @record Dictionary, Line to add to the database
# -----------------------------------------------------------
def insert_record(table_name: str, record: dict):
    engine=create_engine(getenv("DATABASE_URL"))
    meta = MetaData()
    table = Table(table_name, meta, autoload=True, autoload_with=engine)
    with engine.connect() as con:
        con.execute(table.insert(), record)


# -----------------------------------------------------------
# Update the line from the selected table
# Usage : insert_record("user",{"username": "Johny"}, 48)

# @table_name String,
# @record Dictionary, New datas
# @id Integer, Corresponding Id to update
# -----------------------------------------------------------
def update_record(table_name: str, record: dict, id: int):
    engine=create_engine(getenv("DATABASE_URL"))
    meta = MetaData()
    table = Table(table_name, meta, autoload=True, autoload_with=engine)
    stmt = table.update().where(table.c.id == id).values(record)
    engine.execute(stmt)


# -----------------------------------------------------------
# Delete the line from the selected table
# Usage : 

# @table_name String,
# @id Integer, Corresponding Id to delete
# -----------------------------------------------------------
def delete_record(table_name: str, id: int):
    return id


# -----------------------------------------------------------
# Return the line 
# Usage : 

# @table_name String,
# @id Integer, Id to be selected
# -----------------------------------------------------------
def get_by_id(table_name: str, id: int):
    return id
