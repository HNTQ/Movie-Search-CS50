from werkzeug.security import check_password_hash, generate_password_hash
from helpers import generate_code, send_activation_mail
from sqlalchemy import create_engine, MetaData, Table
from os import getenv
from cs50 import SQL


db = SQL("sqlite:///application.db")

class User:

    def get(user_id):
        return user_id


    def add_new(password: str, username: str, email: str):
        hash_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        insert_record(
            "user",
            {"username": username, 
            "hash": hash_password, 
            "email": email.lower()}
        )

        # Activation by email
        code = generate_code(8)
        send_activation_mail(email, username, code)

        # Save activation code
        user = get_by_keyword("user", "email", email.lower()).first()

        insert_record(
            "activation",
            {"user_id": user.id, "activation_code": code}
        )


    def update_email(email: str, id: str):
        update_record("user", {"email": email}, id)


    def update_password(password: str, id: int):
        hash_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        update_record("user", {"hash": hash_password}, id)


    def get_email(id: int):
        user = get_by_id("user", id).first()
        return str(user.email)


    def check_credentials(email: str, password: str):
        message = ""
        # Query database for email
        user = get_by_keyword("user", "email", email).first()

        # Ensure username exists and password is correct
        if not user or not check_password_hash(user.hash, password):
                message = "Invalid username and/or password"

        return {
            "user": user if user else "error",
            "message": message
        }


    def is_single_email(email: str):
        res = get_by_keyword("user", "email", email).first()
        return "Email already used" if res else None
        # return True if res else False
        


    def activate(email: str, code: str):
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
#  # - SHORTHANDS
# ///////////////////////////


# Usage : insert_record("user",{"username": "John","email": "john@email.com"})
# -----------------------------------------------------------
def insert_record(table_name: str, record: dict):
    """ Insert line(s) in the selected table """

    engine = create_engine(getenv("DATABASE_URL"))
    meta = MetaData()
    table = Table(table_name, meta, autoload=True, autoload_with=engine)
    with engine.connect() as con:
        con.execute(table.insert(), record)


# Usage : insert_record("user",{"username": "Johny"}, 48)
# -----------------------------------------------------------
def update_record(table_name: str, record: dict, id: int):
    """ Update the line from the selected table """

    engine = create_engine(getenv("DATABASE_URL"))
    meta = MetaData()
    table = Table(table_name, meta, autoload=True, autoload_with=engine)
    stmt = table.update().where(table.c.id == id).values(record)
    engine.execute(stmt)


# Usage : 
# -----------------------------------------------------------
def delete_record(table_name: str, id: int):
    """ Delete record from the selected table/id """
    return id


# Usage : 
# -----------------------------------------------------------
def get_by_id(table_name: str, id: int):
    """ Return the current line from the selected table/id """

    engine = create_engine(getenv("DATABASE_URL"))
    meta = MetaData()
    table = Table(table_name, meta, autoload=True, autoload_with=engine)
    stmt = table.select().where(table.c.id == id)
    res = engine.execute(stmt)

    return res

# Usage : 
# -----------------------------------------------------------
def get_by_keyword(table_name: str, key: str, value):
    """ Return the current line from the selected table/keyword """
    engine = create_engine(getenv("DATABASE_URL"))
    meta = MetaData()
    table = Table(table_name, meta, autoload=True, autoload_with=engine)
    stmt = table.select().where(table.c[key] == value)
    res = engine.execute(stmt)

    return res
