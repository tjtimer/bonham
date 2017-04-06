from collections import Iterable

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


def table_name(value):
    table_name = ''.join(value.replace(letter, f"_{letter.lower()}")
                         for letter in value[1:] if ord(letter) in range(65, 91))
    return table_name.lower()


class Connect(object):
    @declared_attr
    def __tablename__(cls):
        return table_name(cls.__name__)

    id = sa.Column(sa.Integer, index=True, primary_key=True, autoincrement=True, unique=True)


class BaseModel(object):
    @declared_attr
    def __tablename__(cls):
        return table_name(cls.__name__)

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

    async def create(self, connection, *, data: dict = None) -> dict:
        try:
            stmt = self.__table__.insert().values(**data).returning(self.__table__)
            statement = str(stmt.compile(compile_kwargs={'literal_binds': True}))
            row = await connection.fetchrow(statement)
            return dict(row)
        except Exception as e:
            raise

    async def get_by_id(self, connection: Connection, *, object_id: int = None, fields: list = None) -> dict:
        if fields is None:
            fields = ['*']
        try:
            statement = f"SELECT {', '.join(fields)} FROM {self.__table__} WHERE id={object_id}"
            row = await connection.fetchrow(statement)
            if row:
                return dict(row)
            return None
        except Exception as e:
            raise

    async def get(self, connection: Connection, **kwargs) -> Iterable:
        keys = kwargs.keys()
        if 'fields' not in keys:
            kwargs['fields'] = '*'
        stmt = f"SELECT {kwargs['fields']} FROM {self.__table__} "
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
        stmt += f" ORDER BY {kwargs['order_by']} OFFSET {kwargs['offset']} LIMIT {kwargs['limit']} {kwargs[" \
                f"'direction']}"
        try:
            return (dict(row) for row in await connection.fetch(stmt))
        except Exception as e:
            raise

    async def update(self, connection: Connection, *, key: str = None, data: dict = None) -> dict:
        if key is None:
            key = 'id'
        u_data = {col_name: value for col_name, value in data.items()
                  if
                  col_name in self.__table__.c.keys() and col_name not in ['created', 'id', key] and value is not None}
        stmt = self.__table__.update().where(
                self.__table__.c[key] == data[key]
                ).values(**u_data).returning(self.__table__)
        try:
            statement = str(stmt.compile(compile_kwargs={'literal_binds': True}))
            row = await connection.fetchrow(statement)
            return dict(row)
        except TypeError:
            raise TypeError(f"Update {self.__table__} error. Record with {key} = {data[key]} not found.")
        except Exception as e:
            raise

    async def delete(self, connection, *, object_id: int = None) -> bool:
        try:
            statement = f"DELETE FROM {self.__table__} WHERE id={object_id}"
            await connection.execute(statement)
            return True
        except Exception as e:
            return False
