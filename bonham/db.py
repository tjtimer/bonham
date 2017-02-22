import arrow
import sqlalchemy as sa
import sqlamp
from sqlalchemy import select
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy_utils import ArrowType, ChoiceType

from .constants import PrivacyStatus
from .settings import DSN

Base = declarative_base(metaclass=sqlamp.DeclarativeMeta)


def create_tables(*, models=None):
    engine = sa.create_engine(DSN, client_encoding='utf8', echo=True)
    for model in models:
        model.metadata.bind = engine
        model.metadata.create_all()
    return models


def ForeignKey(related, ondelete=None, onupdate=None, primary_key=None):
    if ondelete is None:
        ondelete = "CASCADE"
    if onupdate is None:
        onupdate = "CASCADE"
    if primary_key is None:
        primary_key = True
    return sa.Column(sa.Integer, sa.ForeignKey('{}.id'.format(related), ondelete=ondelete, onupdate=onupdate),
                     primary_key=primary_key)


class BaseModel(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    @declared_attr
    def id(self):
        return sa.Column(sa.Integer, primary_key=True, autoincrement=True, unique=True)

    @declared_attr
    def last_updated(self):
        return sa.Column(ArrowType, nullable=True)

    @declared_attr
    def created(self):
        return sa.Column(ArrowType)

    @declared_attr
    def privacy(self):
        return sa.Column(ChoiceType(PrivacyStatus, impl=sa.Integer()))

    def __init__(self, **kwargs):
        self.__dict__.update({ key: value for key, value in kwargs.items() if key in self.__table__.c.keys() })

    def __str__(self):
        props = { key: value for key, value in self.__dict__.items() }
        return f"<{self.__table__}: {props}>"

    async def create(self, connection):
        keys = self.__table__.c.keys()
        data = {
            key: value for key, value in self.__dict__.items()
            if key in keys
        }
        data['created'] = f"TIMESTAMP \'{arrow.utcnow()}\'"
        try:
            stmt = self.__table__.insert().values(data).returning(self.__table__)
            result = await connection.fetchrow(str(stmt.compile(compile_kwargs={ 'literal_binds': True })))
            return self.__dict__.update(dict(result))
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
            stmt = stmt.where(kwargs['where'])
        if 'order_by' not in k_keys:
            kwargs['order_by'] = 'id'
        if 'offset' not in k_keys:
            kwargs['offset'] = 0
        if 'limit' not in k_keys:
            kwargs['limit'] = 1000
        stmt = stmt.order_by(kwargs['order_by']).offset(kwargs['offset']).limit(kwargs['limit'])
        try:
            statement = str(stmt.compile(compile_kwargs={ 'literal_binds': True }))
            return ({ key: value for key, value in row.items() } for row in await
            connection.fetch(statement))
        except Exception as e:
            print(f"get {self.__table__}s exception: {type(e).__name__} -> {e}")
            raise

    async def update(self, connection, key=None):
        self.last_updated = f"TIMESTAMP \'{arrow.utcnow().to('local').to('utc').format('YYYY-MM-DD HH:mm:ss')}\'"
        data = { key: value for key, value in self.__dict__.items() if key in self.__table__.c.keys() and value is not
                 None }
        if key is None:
            stmt = self.__table__.update().where(self.__table__.c.id == self.id).values(
                    data).returning(self.__table__)
        else:
            stmt = self.__table__.update().where(self.__table__.c[key] == self.__dict__[key]).values(
                    data).returning(self.__table__)
        try:
            result = await connection.fetchrow(str(stmt.compile(compile_kwargs={ 'literal_binds': True })))
            return self.__dict__.update(dict(result))
        except Exception as e:
            print('\nupdate {} exception: {}\n'.format(self.__table__, type(e).__name__))
            raise

    async def delete(self, connection):
        stmt = self.__table__.delete().where(self.__table__.c.id == self.id)
        try:
            await connection.execute(str(stmt.compile(compile_kwargs={ 'literal_binds': True })))
            del self
            return
        except Exception as e:
            print('\ndelete {} exception: {}\n'.format(self.__table__, e))
            raise

    async def clean_data(self):
        data = self.__dict__
        data['privacy'] = PrivacyStatus(data['privacy']).label
        data['created'] = arrow.get(data['created']).humanize()
        if data['last_updated']:
            data['last_updated'] = arrow.get(data['last_updated']).humanize()
        for key, value in data.items():
            if 'datetime' in str(type(value)):
                data[key] = arrow.get(value).format('YYYY-MM-DD HH:mm:ss')
        return data

    async def serialized(self):
        clean_data = await self.clean_data()
        return { key: value for key, value in clean_data.items() if key in self.__table__.c.keys() }
