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
    engine = sa.create_engine(DSN, client_encoding='utf8')
    for model in models:
        model.metadata.bind = engine
        model.metadata.create_all()


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
        return sa.Column(ArrowType)

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
        data = { key: value for key, value in self.__dict__.items() if key in self.__table__.c.keys() }
        # data['created'] = arrow.now()
        stmt = self.__table__.insert().values(data).returning(self.__table__)
        try:
            _result = await connection.execute(stmt)
            result = await _result.fetchrow()
            self.__dict__.update(dict(result))
        except Exception as e:
            print('\ncreate {} exception: {}\n'.format(self.__table__, e))
            raise
        finally:
            print('create {} done!'.format(self.__table__))

    async def delete(self, connection):
        stmt = self.__table__.delete().where(self.__table__.c.id == self.id)
        try:
            await connection.execute(stmt)
        except Exception as e:
            print('\ndelete {} exception: {}\n'.format(self.__table__, e))
            raise

    async def get(self, connection, **kwargs):
        if 'fields' not in kwargs.keys():
            stmt = self.__table__.select()
        else:
            stmt = select([self.__table__.c[key] for key in kwargs['fields'].split(',')])
        if 'order_by' not in kwargs.keys():
            kwargs['order_by'] = 'id'
        if 'limit' not in kwargs.keys():
            kwargs['limit'] = 1000
        if 'offset' not in kwargs.keys():
            kwargs['offset'] = 0

        print(stmt)
        if 'where' in kwargs.keys():
            stmt.where(kwargs['where'])
        stmt.order_by(kwargs['order_by']).offset(kwargs['offset']).limit(kwargs['limit'])
        try:
            print()
            statement = stmt.compile(compile_kwargs={ 'literal_binds': True })
            print(statement)
            return ({ key: value for key, value in item.items() } for item in await connection.fetch(str(statement)))
        except Exception as e:
            print('\nget all {}s exception: {}\n'.format(self.__table__, e))
            raise

    async def update(self, connection, key=None):
        data = { key: value for key, value in self.__dict__.items() if key in self.__table__.c.keys() and value is not
                 None }
        data['last_updated'] = arrow.utcnow()
        if key is None:
            print(self.__dict__, data)
            stmt = self.__table__.update().where(self.__table__.c.id == self.id).values(
                    data).returning(self.__table__)
        else:
            stmt = self.__table__.update().where(self.__table__.c[key] == self.__dict__[key]).values(
                    data).returning(self.__table__)
        try:
            r_proxy = await connection.execute(stmt)
            result = await r_proxy.fetchone()
            self.__dict__.update(dict(result))
        except Exception as e:
            print('\nupdate {} exception: {}\n'.format(self.__table__, type(e).__name__))
            raise

    async def save(self, connection):
        try:
            await self.update(connection)
        except TypeError:
            await self.create(connection)

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
