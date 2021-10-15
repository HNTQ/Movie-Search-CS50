from werkzeug.security import check_password_hash, generate_password_hash
from helpers import generate_code, send_activation_mail
from sqlalchemy import create_engine, MetaData, Table
from uuid import uuid4
from os import getenv


class User:
    """All required methods to handle users"""

    # Add a new user
    def add_new(password: str, username: str, email: str):
        hash_password = generate_password_hash(
            password, method="pbkdf2:sha256", salt_length=8
        )
        user_id = str(uuid4())
        insert_record(
            "users",
            {
                "id": user_id,
                "username": username,
                "hash": hash_password,
                "email": email.lower(),
            },
        )

        # Activation by email
        code = generate_code(8)
        send_activation_mail(email, username, code)

        # Save activation code
        insert_record("activation", {"user_id": user_id, "activation_code": code})

    # Update email by id
    def update_email(email: str, id: str):
        update_record("users", {"email": email}, id)

    # Update the password by id
    def update_password(password: str, id: int):
        hash_password = generate_password_hash(
            password, method="pbkdf2:sha256", salt_length=8
        )
        update_record("users", {"hash": hash_password}, id)

    # Look for an email by id
    def get_email(id: str):
        user = get_record("users", "id", id)
        return str(user.email)

    # Do the required test on password
    def check_credentials(email: str, password: str):
        message = ""
        # Query database for email
        user = get_record("users", "email", email)

        # Ensure username exists and password is correct
        if not user or not check_password_hash(user.hash, password):
            message = "credential_error"

        return {"user": user if user else "error", "message": message}

    # Check if an email taken
    def email_exist(email: str):
        return record_exist("users", "email", email)

    # Activate a verified account
    def activate(email: str, code: str):
        user = get_record("users", "email", email.lower())
        row = get_record("activation", "user_id", user.id or None)

        if user and user.active == 1:
            return "already_activated"
        if not row or row.activation_code != code:
            return "invalid_activation"

        delete_records("activation", "id", row.id)
        update_record("users", {"active": True}, user.id)

    def delete_account(id: str):
        if get_record("users", "id", id):
            delete_records("users", "id", id)
            return True
        return False


# ///////////////////////////
#  # - SHORTHANDS
# ///////////////////////////


# Usage : insert_record("users",{"username": "John","email": "john@email.com"})
# -----------------------------------------------------------
def insert_record(table_name: str, record: dict):
    """Insert line(s) in the selected table"""
    if not "id" in record:
        record["id"] = str(uuid4())
    engine = create_engine(getenv("SQLALCHEMY_DATABASE_URL"))
    meta = MetaData()
    table = Table(table_name, meta, autoload=True, autoload_with=engine)
    with engine.connect() as con:
        con.execute(table.insert(), record)


# Usage : update_record("users",{"username": "Johny"}, 48)
# -----------------------------------------------------------
def update_record(table_name: str, record: dict, id: int):
    """Update the line from the selected table"""

    engine = create_engine(getenv("SQLALCHEMY_DATABASE_URL"))
    meta = MetaData()
    table = Table(table_name, meta, autoload=True, autoload_with=engine)
    stmt = table.update().where(table.c.id == id).values(record)
    engine.execute(stmt)


# Usage : delete_records("users", "id", 48)
# Usage : delete_record("users", "username", "John")
# -----------------------------------------------------------
def delete_records(table_name: str, key: str, value: str):
    """Delete multiple records from the selected table/id"""

    engine = create_engine(getenv("SQLALCHEMY_DATABASE_URL"))
    meta = MetaData()
    table = Table(table_name, meta, autoload=True, autoload_with=engine)
    stmt = table.delete().where(table.c[key] == value)
    engine.execute(stmt)


# Usage : get_record("users", "email", "john@email.com")
# Usage : get_record("users","id", 48)
# -----------------------------------------------------------
def get_record(table_name: str, key: str, value, first=True):
    """Return the current line from the selected table/keyword"""

    engine = create_engine(getenv("SQLALCHEMY_DATABASE_URL"))
    meta = MetaData()
    table = Table(table_name, meta, autoload=True, autoload_with=engine)
    stmt = table.select().where(table.c[key] == value)
    res = engine.execute(stmt)

    if first:
        return res.first()

    return res


# Usage : record_exist("users","id", 48)
# -----------------------------------------------------------
def record_exist(table_name: str, key: str, value):
    """Return a boolean if the record exist"""
    res = get_record(table_name, key, value)
    return True if res else False
