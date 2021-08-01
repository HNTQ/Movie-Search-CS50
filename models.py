from werkzeug.security import check_password_hash, generate_password_hash
from helpers import generate_code, send_activation_mail
from sqlalchemy import create_engine, MetaData, Table
from os import getenv


class User:
    def add_new(password: str, username: str, email: str):
        hash_password = generate_password_hash(
            password, method="pbkdf2:sha256", salt_length=8
        )
        insert_record(
            "user",
            {"username": username, "hash": hash_password, "email": email.lower()},
        )

        # Activation by email
        code = generate_code(8)
        send_activation_mail(email, username, code)

        # Save activation code
        user = get_record("user", "email", email.lower()).first()

        insert_record("activation", {"user_id": user.id, "activation_code": code})

    def update_email(email: str, id: str):
        update_record("user", {"email": email}, id)

    def update_password(password: str, id: int):
        hash_password = generate_password_hash(
            password, method="pbkdf2:sha256", salt_length=8
        )
        update_record("user", {"hash": hash_password}, id)

    def get_email(id: int):
        user = get_record("user", "id", id).first()
        return str(user.email)

    def check_credentials(email: str, password: str):
        message = ""
        # Query database for email
        user = get_record("user", "email", email).first()

        # Ensure username exists and password is correct
        if not user or not check_password_hash(user.hash, password):
            message = "credential_error"

        return {"user": user if user else "error", "message": message}

    def email_exist(email: str):
        return record_exist("user", "email", email)

    def activate(email: str, code: str):
        user = get_record("user", "email", email.lower()).first()
        row = get_record("activation", "user_id", user.id or None).first()

        if user and user.active == 1:
            return "already_activated"
        if not row or row.activation_code != code:
            return "invalid_activation"

        delete_records("activation", "id", row.id)
        update_record("user", {"active": True}, user.id)


# ///////////////////////////
#  # - SHORTHANDS
# ///////////////////////////


# Usage : insert_record("user",{"username": "John","email": "john@email.com"})
# -----------------------------------------------------------
def insert_record(table_name: str, record: dict):
    """Insert line(s) in the selected table"""

    engine = create_engine(getenv("DATABASE_URL"))
    meta = MetaData()
    table = Table(table_name, meta, autoload=True, autoload_with=engine)
    with engine.connect() as con:
        con.execute(table.insert(), record)


# Usage : update_record("user",{"username": "Johny"}, 48)
# -----------------------------------------------------------
def update_record(table_name: str, record: dict, id: int):
    """Update the line from the selected table"""

    engine = create_engine(getenv("DATABASE_URL"))
    meta = MetaData()
    table = Table(table_name, meta, autoload=True, autoload_with=engine)
    stmt = table.update().where(table.c.id == id).values(record)
    engine.execute(stmt)


# Usage : delete_records("user", "id", 48)
# Usage : delete_record("user", "username", "John")
# -----------------------------------------------------------
def delete_records(table_name: str, key: str, value: str):
    """Delete multiple records from the selected table/id"""

    engine = create_engine(getenv("DATABASE_URL"))
    meta = MetaData()
    table = Table(table_name, meta, autoload=True, autoload_with=engine)
    stmt = table.delete().where(table.c[key] == value)
    engine.execute(stmt)


# Usage : get_record("user", "email", "john@email.com")
# Usage : get_record("user","id", 48)
# -----------------------------------------------------------
def get_record(table_name: str, key: str, value):
    """Return the current line from the selected table/keyword"""

    engine = create_engine(getenv("DATABASE_URL"))
    meta = MetaData()
    table = Table(table_name, meta, autoload=True, autoload_with=engine)
    stmt = table.select().where(table.c[key] == value)
    res = engine.execute(stmt)

    return res


# Usage : record_exist("user","id", 48)
# -----------------------------------------------------------
def record_exist(table_name: str, key: str, value):
    """Return a boolean if the record exist"""
    res = get_record(table_name, key, value).first()
    return True if res else False
