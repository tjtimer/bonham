from typing import Any

import sqlalchemy as sa
import sqlamp
from asyncpg.connection import Connection
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy_utils import ArrowType, ChoiceType

from bonham.core import pg_db
from bonham.core.constants import Privacy
from bonham.core.utils import snake_case

__all__ = ['Base', 'BaseModel', 'Connect']

Base = declarative_base(metaclass=sqlamp.DeclarativeMeta)



def bind_models(models, engine):
    for model in models:
        model.metadata.bind = engine
        model.metadata.create_all()

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
        return snake_case(cls.__name__)

    id = sa.Column(sa.Integer, index=True, primary_key=True, autoincrement=True, unique=True)

    async def get_or_create(self, connection: Connection, *, data: dict = None) -> dict:
        table = self.__table__
        where = ','.join([f"{key}={value}" for key, value in data.items()
                          if key in table.c.keys() and value is not None])
        stmt = f"SELECT * FROM {table} WHERE {where}'"
        row = await connection.fetchrow(stmt)
        if not row:
            columns = ','.join(data.keys())
            values = ','.join([str(value) for value in data.values()])
            stmt = f"INSERT INTO {self.__tablename__} ({columns}, created) VALUES ({values}, DEFAULT) RETURNING *"
            row = await connection.fetchrow(stmt)
        return dict(row)


class BaseModel(object):
    """
        Parent class Models.

        Usage:
            Model definition:
                class MyModel(Base, BaseModel):
                    ...

            creating:
                model = MyModel(**data)
                entry = await model.create(connection, data=dict(data))

            updating an existing entry:
                entry = await MyModel().update(connection, ref=<str: column_name>, data=dict(data))
                where ref is optional and defaults to 'id'

        Models inheriting from BaseModel will have

            following columns:
                id, privacy, created, last_updated

            following methods:
                create, update, delete, get, get_by_id, get_by_key

                where create, update, delete and get_by_id return dictionaries or None
                while get returns a generator if record(s) exists or None if not,
                and get_by_key will return a dict or None by default but can return a generator if many=True.
    """

    @declared_attr
    def __tablename__(cls):
        return snake_case(cls.__name__)

    id = sa.Column(sa.Integer, index=True, primary_key=True, autoincrement=True, unique=True)

    @declared_attr
    def privacy(self):
        return sa.Column(ChoiceType(Privacy, impl=sa.Integer()), server_default='7')  # default is private

    @declared_attr
    def created(self):
        return sa.Column(ArrowType(timezone=True), server_default=sa.func.current_timestamp())

    @declared_attr
    def last_updated(self):
        return sa.Column(ArrowType(timezone=True), nullable=True, onupdate=sa.func.current_timestamp())

    @declared_attr
    def update_count(self):
        return sa.Column(sa.Integer, server_default='0')

    @declared_attr
    def disabled(self):
        return sa.Column(ArrowType)

    def __init__(self, **kwargs):
        vars(self).update({key: value for key, value in kwargs.items()
                           if key in self.__table__.c.keys() and value is not None})

    def __str__(self):
        table = self.__table__
        return f"<{table}: {vars(self)}>"

    async def create(self, connection, **kwargs):
        data = kwargs.pop('data', {key: value for key, value in vars(self).items()
                                   if key in self.__table__.c.keys() and value is not None})

        result = await pg_db.create(connection, self.__table__, data=data, **kwargs)
        return dict(result)

    async def update(self, connection, **kwargs):
        print(f"BaseModel update:\n\tkwargs: {kwargs}")
        data = kwargs.pop('data', {key: value for key, value in vars(self).items()
                                   if key in self.__table__.c.keys() and value is not None})
        print(f"\n\nbase model update data: {data}")
        result = await pg_db.update(connection, self.__table__, data=data, **kwargs)
        print(result)
        return result

    async def delete(self, connection, **kwargs):
        o_id = kwargs.pop('o_id', self.id)
        if o_id is None:
            raise TypeError(f"kwargs.pop('o_id', self.id) must not return None. You have to set one of them!")
        result = await pg_db.delete(connection, self.__table__, o_id=o_id)
        return result

    async def get(self, connection, **kwargs):
        where = kwargs.pop('where', None)
        result = await pg_db.get(connection, self.__table__, where=where, **kwargs)
        return result

    async def get_by_id(self, connection, **kwargs):
        o_id = kwargs.pop('o_id', self.id)
        if o_id is None:
            raise TypeError(f"kwargs.pop('o_id', self.id) must not return None. You have to set one of them!")
        result = await pg_db.get_by_id(connection, self.__table__, o_id=o_id, **kwargs)
        return result

    async def get_by_key(self, connection, *, key: str = None, value: Any = None, **kwargs):
        if key is None or not isinstance(key, str):
            raise TypeError(f"{__name__} get_by_key: required keyword argument 'key' is missing or not of type string.")
        if value is None:
            raise TypeError(f"kwargs.pop('value', self.id) must not return None. You have to set one of them!")
        result = await pg_db.get_by_key(connection, self.__table__, key=key, value=value, **kwargs)
        return result

