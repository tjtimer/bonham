from collections import Iterable
from datetime import datetime

import arrow
import asyncpg
from asyncpg.connection import Connection
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy_utils import ArrowType, ChoiceType
import sqlamp

from bonham.constants import PrivacyStatus
from bonham.settings import DSN

__all__ = [
    "Base",
    "BaseModel",
    "ForeignKey",
    "create_tables",
    "drop_tables",
    "create",
    "get",
    "get_by_id",
    "update",
    "delete",
    "serialize",
    "setup"
    ]

Base = declarative_base(metaclass=sqlamp.DeclarativeMeta)


async def setup(app):
    app['db'] = await asyncpg.create_pool(dsn=DSN, loop=app.loop, command_timeout=60)
    #  print("end db setup", flush=True)


def create_tables(*, models=None):
    engine = sa.create_engine(DSN, client_encoding='utf8', echo=True)
    for model in models:
        model.metadata.bind = engine
    Base.metadata.create_all()
    return [model.__table__ for model in models]


def drop_tables(*, tables=None):
    engine = sa.create_engine(DSN, client_encoding='utf8', echo=True)
    connection = engine.connect()
    for table in tables:
        connection.execute(f"DROP TABLE {table} CASCADE")
    connection.close()


def ForeignKey(related, ondelete=None, onupdate=None, primary_key=None):
    if ondelete is None:
        ondelete = "CASCADE"
    if onupdate is None:
        onupdate = "CASCADE"
    if primary_key is None:
        primary_key = True
    return sa.Column(sa.Integer, sa.ForeignKey(f"{related}.id", ondelete=ondelete, onupdate=onupdate),
                     primary_key=primary_key)


class BaseModel(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = sa.Column(sa.Integer, index=True, primary_key=True, autoincrement=True, unique=True)

    @declared_attr
    def last_updated(self):
        return sa.Column(ArrowType(timezone=True), nullable=True, onupdate=sa.func.current_timestamp())

    @declared_attr
    def created(self):
        return sa.Column(ArrowType(timezone=True), default=sa.func.current_timestamp())

    @declared_attr
    def privacy(self):
        return sa.Column(ChoiceType(PrivacyStatus, impl=sa.Integer()), server_default='7')  # default is private

    def __str__(self):
        return f"<{self.__table__}: {vars(self)}>"


class Association(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = sa.Column(sa.Integer, index=True, primary_key=True, autoincrement=True, unique=True)


async def create(connection, *, table: sa.Table = None, data: dict = None) -> dict:
    try:
        stmt = table.insert().values(**data).returning(table)
        statement = str(stmt.compile(compile_kwargs={'literal_binds': True}))
        #  print(statement)
        row = await connection.fetchrow(statement)
        #  print(row)
        return dict(row)
    except Exception as e:
        #  print(f"Exception at create {table}: {type(e).__name__} -> {e}")
        raise


async def get_by_id(connection: Connection, *, table: sa.Table = None, object_id: int = None,
                    fields: list = None) -> dict:
    if fields is None:
        fields = ['*']
    try:
        statement = f"SELECT {', '.join(fields)} FROM {table} WHERE id={object_id}"
        row = await connection.fetchrow(statement)
        if row:
            return dict(row)
        return None
    except Exception as e:
        #  print(f"Exception at get_by_id {table}: {type(e).__name__}: {e}")
        raise


async def get(connection: Connection, *, table: sa.Table = None, **kwargs) -> Iterable:
    keys = kwargs.keys()
    if 'fields' not in keys:
        kwargs['fields'] = '*'
    stmt = f"SELECT {kwargs['fields']} FROM {table} "
    if 'where' in keys:
        stmt += f" WHERE {kwargs['where']} "
    if 'order_by' not in keys:
        kwargs['order_by'] = 'id'
    if 'offset' not in keys:
        kwargs['offset'] = 0
    if 'limit' not in keys:
        kwargs['limit'] = 1000
    if 'direction' not in keys:
        kwargs['direction'] = ""
    stmt += f" ORDER BY {kwargs['order_by']} OFFSET {kwargs['offset']} LIMIT {kwargs['limit']} {kwargs['direction']}"
    try:
        #  print(stmt, flush=True)
        return (dict(row) for row in await connection.fetch(stmt))
    except Exception as e:
        #  print(f"Exception at get {table}: {type(e).__name__}: {e}")
        raise


async def update(connection: Connection, *, table: sa.Table = None, key: str = None, data: dict = None) -> dict:
    if key is None:
        key = 'id'
    u_data = {col_name: value for col_name, value in data.items()
              if col_name in table.c.keys() and col_name not in ['created', 'id', key] and value is not None}
    stmt = table.update().where(
            table.c[key] == data[key]
            ).values(**u_data).returning(table)
    #  print(f"update:\n\tdata: {data}\n\tkey: {key}\n\tstmt: {stmt}")
    try:
        statement = str(stmt.compile(compile_kwargs={'literal_binds': True}))
        #  print(f"update statement:\n\t{statement}")
        row = await connection.fetchrow(statement)
        return dict(row)
    except TypeError:
        #  print(f"update got TypeError")
        raise TypeError(f"Update {table} error. Record with {key} = {data[key]} not found.")
    except Exception as e:
        #  print(f"update {table} exception: {type(e).__name__}: {e}", flush=True)
        raise


async def delete(connection, *, table: str = None, object_id: int = None) -> bool:
    try:
        statement = f"DELETE FROM {table} WHERE id={object_id}"
        await connection.execute(statement)
        return True
    except Exception as e:
        #  print(f'delete {table} exception: {e}')
        return False


async def serialize(data: dict) -> dict:
    keys = data.keys()
    if 'password' in keys:
        del data['password']
    if 'privacy' in keys:
        data['privacy'] = PrivacyStatus(data['privacy']).label
    if 'created' in keys:
        data['created'] = [arrow.get(data['created']).humanize(), arrow.get(data['created']).for_json()]
    if 'last_updated' in keys:
        data['last_updated'] = [arrow.get(data['last_updated']).humanize(), arrow.get(data['last_updated']).for_json()]
    for key, value in data.items():
        if isinstance(value, (datetime, arrow.arrow.Arrow)):
            data[key] = arrow.get(value).for_json()
    return data
