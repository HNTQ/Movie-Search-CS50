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
            }
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
    def update_password(password: str, id: str):
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
        if record_exist("users", "id", id):
            delete_records("users", "id", id)
            return True
        return False

class List: 

    # Add a new list
    def add_new(user_id: str, name: str, category="Classics"):
        list_id = str(uuid4())
        insert_record(
            "lists",
            {
                "id": list_id,
                "name": name,
                "category": category,
                "user_id": user_id,
            }
        )

    # Delete a list
    def delete_list(list_id: str):
        if record_exist("lists", "id", list_id):
            delete_records("lists", "id", list_id)
            return True
        return False

    # Rename a list 
    def rename_list(list_id: str, name: str):
        update_record("lists",{"name": name}, list_id)

    # Change category 
    def rename_category(list_id: str, category: str):
        update_record("lists",{"category": category}, list_id)

    # Get list details (name, category)
    def get_lists(list_id: str):
        return get_record("lists","user_id", list_id)

    # Get all lists created by an user
    def get_lists(user_id: str):
        return get_record("lists","user_id", user_id, False)

    # Get list movies details
    def get_list_movies(list_id: str):
        return get_record("lists_movies","id", list_id, False)

    # Add movie into a list
    def add_movie(list_id: str, movie_id: str):
        id = str(uuid4())
        insert_record(
            "lists_movies",
            {
                "id": id,
                "list_id": list_id,
                "movie_id": movie_id
            }
        )

    # Remove movie from a list
    def delete_movie_from_list(list_id: str, movie_id: str):
        print("remove movie")
        #necessitera de créer un delete_record multi parametre "where list_id = xxx and movie_id = xxx"

class Movie:

    # Add a movie
    def add_new(movie_tmdb_id: int, name: str, description: str, duration: str, poster: str):
        movie_id = str(uuid4())
        insert_record(
            "movies",
            {
                "id": movie_id,
                "name": name,
                "movie_tmdb_id": name,
                "description": category,
                "duration": user_id,
                "poster": poster
            }
        )

    # Delete a movie, used only if none list references this movie
    def delete_movie(movie_id: str):
        if record_exist("movies", "id", movie_id):
            delete_records("movies", "id", movie_id)
            return True
        return False

    # Get detail of one movie
    def get_movie(movie_id: str):
        return get_record("movies","id", movie_id)


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
