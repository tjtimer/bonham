import asyncpg
from asyncpg.connection import Connection
import sqlalchemy as sa
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
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
        return cls.__name__.lower()

    id = sa.Column(sa.Integer, index=True, primary_key=True, autoincrement=True, unique=True)


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

    async def create(self, connection):
        keys = self.__table__.c.keys()
        data = {
            key: value for key, value in vars(self).items()
            if key in keys
            }
        data['created'] = f"TIMESTAMP \'{arrow.utcnow()}\'"
        try:
            stmt = self.__table__.insert().values(data).returning(self.__table__)
            result = await connection.fetchrow(str(stmt.compile(compile_kwargs={'literal_binds': True})))
            return vars(self).update(dict(result))
        except Exception as e:
            print(f'create {self.__table__} exception: {type(e).__name__} -> {e}')
            raise

    async def get(self, connection, **kwargs):
        k_keys = kwargs.keys()
        if 'fields' not in k_keys:
            stmt = self.__table__.select()
        else:
            stmt = select([self.__table__.c[key] for key in kwargs['fields'].split(',')])
        if 'where' in k_keys:
            stmt = stmt.where(sa.text(kwargs['where']))
        if 'order_by' not in k_keys:
            kwargs['order_by'] = 'id'
        if 'offset' not in k_keys:
            kwargs['offset'] = 0
        if 'limit' not in k_keys:
            kwargs['limit'] = 1000
        stmt = stmt.order_by(kwargs['order_by']).offset(kwargs['offset']).limit(kwargs['limit'])
        try:
            statement = str(stmt.compile(compile_kwargs={'literal_binds': True}))
            return ({key: value for key, value in row.items()} for row in await connection.fetch(statement))
        except Exception as e:
            print(f"get {self.__table__}s exception: {type(e).__name__}: {e}")
            raise

    async def update(self, connection, key=None):
        self.last_updated = f"TIMESTAMP \'{arrow.utcnow()}\'"
        data = {key: value for key, value in vars(self).items() if key in self.__table__.c.keys() and value is not
                None}
        if key is None:
            key = 'id'
        stmt = self.__table__.update().where(self.__table__.c[key] == vars(self)[key]).values(
                data).returning(self.__table__)
        try:
            result = await connection.fetchrow(str(stmt.compile(compile_kwargs={'literal_binds': True})))
            return vars(self).update(dict(result))
        except TypeError as e:
            raise IntegrityError(f"Update {self.__table__} error. Record with {key} = {vars(self)[key]} not found.",
                                 type(e).__name__,
                                 e)
        except Exception as e:
            print(f"update {self.__table__} exception: {type(e).__name__}: {e.value}", flush=True)
            raise

    async def delete(self, connection):
        stmt = self.__table__.delete().where(self.__table__.c.id == self.id)
        try:
            statement = str(stmt.compile(compile_kwargs={'literal_binds': True}))
            await connection.execute(statement)
            del self
            return
        except Exception as e:
            print(f'delete {self.__table__} exception: {e}')
            raise


async def check_existence(self, connection: Connection, *, object_id: int = None, fields: list = None) -> dict:
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
