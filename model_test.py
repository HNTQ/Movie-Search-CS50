from models import insert_record, update_record, delete_records, get_record
import sqlalchemy as sa
import uuid
from os import getenv, environ


environ["DATABASE_URL"] = "sqlite:///test.db"

def test_createTable():
    table_name = uuid.uuid4()
    engine = sa.create_engine(getenv("DATABASE_URL"))
    meta = sa.MetaData()
    sa.Table(
        table_name, 
        meta,
        sa.Column("username",
        sa.String(255)))
    meta.create_all(engine)
    
    #test if table is in database
    assert table_name in meta.tables.keys()
    assert not "coucou" in meta.tables.keys()

def test_insert_update():
    table_name = uuid.uuid4()
    engine = sa.create_engine(getenv("DATABASE_URL"))
    meta = sa.MetaData()
    sa.Table(
        table_name, 
        meta,
        sa.Column("username",
        sa.String(255)),
        sa.Column("id",
        sa.String(255),
        primary_key=True))
    meta.create_all(engine)

    id_test = str(uuid.uuid4())
    #test insert with id
    insert_record(table_name,{"username":"foo", "id": id_test})
    #test insert without id
    insert_record(table_name,{"username":"john"})
    #test update
    update_record(table_name, {"username":"bar"}, id_test)

    first_insert = get_record(table_name, "id", id_test)
    second_insert = get_record(table_name, "username", "john")
    table_length = sa.Table(table_name, meta, autoload_with=engine)
    assert first_insert.username == "bar"
    assert second_insert.username == "john"


def test_delete_record():
    table_name = uuid.uuid4()
    engine = sa.create_engine(getenv("DATABASE_URL"))
    meta = sa.MetaData()
    sa.Table(
        table_name, 
        meta,
        sa.Column("username",
        sa.String(255)),
        sa.Column("id",
        sa.String(255),
        primary_key=True))
    meta.create_all(engine)

    id_test = str(uuid.uuid4())
    insert_record(table_name,{"username":"foo", "id": id_test})
    #test delete function
    delete_records(table_name, "id", id_test)
    test = get_record(table_name, "id", id_test)
    assert not test