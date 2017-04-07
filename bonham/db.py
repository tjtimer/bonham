from collections import Iterator

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
    return app


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


class Connect(object):
    """
        Parent class for all Models that connect two Models.
        
        Usage:
            class MyModelConnection(Base, Connect):
                left_id = ForeignKey('left')
                right_id = ForeignKey('right')
    """
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = sa.Column(sa.Integer, index=True, primary_key=True, autoincrement=True, unique=True)

    async def get_or_create(self, connection: Connection, *,
                            data: dict = None) -> dict:
        table = self.__table__
        where = ','.join([f"{key}={value}" for key, value in data.items()
                          if key in table.c.keys() and value is not None])
        stmt = f"SELECT * FROM {table} WHERE {where}'"
        row = await connection.fetchrow(stmt)
        if not row:
            columns = ','.join(data.keys())
            values = ','.join([str(value) for value in data.values()])
            stmt = f"INSERT INTO tag ({columns}, created) VALUES ({values}, DEFAULT) RETURNING *"
            row = await connection.fetchrow(stmt)
        return dict(row)


class BaseModel(object):
    """
        Parent class for all Models that define tables and do not connect Models.
        
        Usage:
            Model definition:
                class MyModel(Base, BaseModel):
                    ...
            
            creating a new table entry:
                entry = await MyModel().create(connection, data=dict(data))
            
            updating an existing entry:
                entry = await MyModel().update(connection, ref=<str: column_name>, data=dict(data))
                
                where ref is optional and defaults to 'id'
        
        Models inheriting from BaseModel will have
        
            following columns:
                id, privacy, created, last_updated
            
            following methods:
                create, update, delete, get_by_id, get
                
                where create, update delete and get_by_id return dict if successful or None if not
                and get returns a generator containing dict(s) if record(s) exists or None if not.
    """
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = sa.Column(sa.Integer, index=True, primary_key=True, autoincrement=True, unique=True)

    @declared_attr
    def privacy(self):
        return sa.Column(ChoiceType(PrivacyStatus, impl=sa.Integer()), server_default='7')  # default is private

    @declared_attr
    def created(self):
        return sa.Column(ArrowType(timezone=True), server_default=sa.func.current_timestamp())

    @declared_attr
    def last_updated(self):
        return sa.Column(ArrowType(timezone=True), nullable=True, onupdate=sa.func.current_timestamp())

    @declared_attr
    def update_count(self):
        return sa.Column(sa.Integer, server_default='0')

    def __str__(self):
        table = self.__table__
        return f"<{table}: {table.c.keys()}>"

    async def create(self, connection, *, data: dict = None) -> dict or None:
        table = self.__table__
        data = {
            key: value for key, value in data.items()
            if key in table.c.keys() and value is not None
            }
        columns = ','.join(data.keys())
        values = ','.join([str(value) for value in data.values()])
        stmt = f"INSERT INTO {table} ({columns}, created) VALUES ({values}, DEFAULT) RETURNING *"
        result = await connection.fetchrow(stmt)
        if result:
            return dict(result)
        else:
            return None

    async def update(self, connection, *, ref=None, data: dict = None):
        table = self.__table__
        if ref is None:
            ref = 'id'
        updates = ','.join(f"{key}={value} " for key, value in data.items()
                           if key in table.c.keys() and key not in [ref, 'id', 'created'] and value is not None)
        defaults = "last_updated=CURRENT_TIMESTAMP, update_count=update_count+1"
        stmt = f"UPDATE {table} SET {updates}, {defaults} WHERE {ref} = {data[ref]} RETURNING *"
        result = await connection.fetchrow(stmt)
        if result:
            return dict(result)
        else:
            return None

    async def delete(self, connection, *,
                     id: int = None) -> dict or None:
        table = self.__table__
        stmt = f"DELETE FROM {table} WHERE id={id} RETURNING *"
        row = await connection.fetchrow(stmt)
        if row:
            return dict(row)
        return None

    async def get(self, connection, *,
                  fields: str = None,
                  where: str = None,
                  order_by: str = None,
                  offset: int = None,
                  limit: int = None) -> Iterator or None:
        table = self.__table__
        if fields is None:
            stmt = f"SELECT * FROM {table} "
        else:
            stmt = f"SELECT {fields} FROM {table} "
        if where is not None:
            stmt += f"WHERE {where} "
        if order_by is None:
            order_by = 'id'
        if offset is None:
            offset = 0
        if limit is None:
            limit = 1000
        stmt += f"ORDER BY {order_by} OFFSET {offset} LIMIT {limit}"
        rows = await connection.fetch(stmt)
        if len(rows):
            return (dict(row) for row in rows)
        return None

    async def get_by_id(self, connection: Connection, *,
                        id=None) -> dict or None:
        table = self.__table__
        stmt = f"SELECT * FROM {table} WHERE id={id}"
        row = await connection.fetchrow(stmt)
        if row:
            return dict(row)
        return None


async def check_existence(connection: Connection, *,
                          table: sa.Table = None,
                          id: int = None) -> bool:
    statement = f"SELECT id FROM {table} WHERE id={id}"
    row = await connection.execute(statement)
    if row:
        return True
    return False
