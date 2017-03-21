import arrow
import asyncpg
import sqlalchemy as sa
import sqlamp
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy_utils import ArrowType, ChoiceType

from bonham.constants import PrivacyStatus
from bonham.settings import DSN

__all__ = [
    "Base",
    "BaseModel",
    "ForeignKey",
    "create_tables",
    ""
    ]

Base = declarative_base(metaclass=sqlamp.DeclarativeMeta)


async def setup(app):
    app['db'] = await asyncpg.create_pool(dsn=DSN, loop=app.loop, command_timeout=60)
    print("end db setup", flush=True)


def create_tables(*, models=None):
    engine = sa.create_engine(DSN, client_encoding='utf8', echo=True)
    for model in models:
        model.metadata.bind = engine
        model.metadata.create_all()
    return models


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
        return sa.Column(ChoiceType(PrivacyStatus, impl=sa.Integer()))

    def __init__(self, **kwargs):
        self.columns = self.__table__.c.keys()
        vars(self).update({key: value for key, value in kwargs.items() if key in self.columns})

    def __str__(self):
        props = {key: value for key, value in vars(self).items()}
        return f"<{self.__table__}: {props}>"

    async def create(self, *, connection=None):
        keys = self.columns
        data = {
            key: value for key, value in vars(self).items()
            if key in keys and value is not None
            }
        try:
            stmt = self.__table__.insert().values(data).returning(self.__table__)
            statement = str(stmt.compile(compile_kwargs={'literal_binds': True}))
            print(statement, flush=True)

            result = await connection.fetchrow(statement)
            return self.__dict__.update(dict(result))
        except Exception as e:
            print(f'create {self.__table__} exception: {type(e).__name__} -> {e}')
            raise

    async def get(self, *, connection=None, **kwargs):
        keys = kwargs.keys()
        if 'fields' not in keys:
            stmt = self.__table__.select()
        else:
            stmt = select([self.__table__.c[key] for key in kwargs['fields'].split(',')])
        if 'where' in keys:
            stmt = stmt.where(sa.text(kwargs['where']))
        if 'order_by' not in keys:
            kwargs['order_by'] = 'id'
        if 'offset' not in keys:
            kwargs['offset'] = 0
        if 'limit' not in keys:
            kwargs['limit'] = 1000
        stmt = stmt.order_by(kwargs['order_by']).offset(kwargs['offset']).limit(kwargs['limit'])
        try:
            statement = str(stmt.compile(compile_kwargs={'literal_binds': True}))
            print(statement, flush=True)
            return ({key: value for key, value in row.items()} for row in await connection.fetch(statement))
        except Exception as e:
            print(f"get {self.__table__}s exception: {type(e).__name__}: {e}")
            raise

    async def update(self, *, connection=None, key=None):
        #  self.last_updated = f"TIMESTAMP \'{arrow.utcnow()}\'"
        data = {key: value for key, value in vars(self).items() if key in self.__table__.c.keys() and value is not
                None}
        if key is None:
            key = 'id'
        stmt = self.__table__.update().where(
                self.__table__.c[key] == vars(self)[key]
                ).values(data).returning(self.__table__)
        try:
            result = await connection.fetchrow(str(stmt.compile(compile_kwargs={'literal_binds': True})))
            return vars(self).update(dict(result))
        except TypeError as e:
            raise IntegrityError(f"Update {self.__table__} error. Record with {key} = {self.__dict__[key]} not found.",
                                 type(e).__name__,
                                 e)
        except Exception as e:
            print(f"update {self.__table__} exception: {type(e).__name__}: {e.value}", flush=True)
            raise

    async def delete(self, *, connection=None):
        stmt = self.__table__.delete().where(self.__table__.c.id == self.id)
        try:
            statement = str(stmt.compile(compile_kwargs={'literal_binds': True}))
            await connection.execute(statement)
            del self
            return
        except Exception as e:
            print(f'delete {self.__table__} exception: {e}')
            raise

    async def clean_data(self):
        data = vars(self)
        if data['privacy']:
            data['privacy'] = PrivacyStatus(data['privacy']).label
        if data['created']:
            data['created'] = arrow.get(data['created']).humanize()
        if data['last_updated']:
            data['last_updated'] = arrow.get(data['last_updated']).humanize()
        for key, value in data.items():
            if 'datetime' in str(type(value)):
                data[key] = arrow.get(value).format('YYYY-MM-DD HH:mm:ss')
        return data

    async def serialized(self):
        clean_data = await self.clean_data()
        return {key: value for key, value in clean_data.items() if key in self.columns}
