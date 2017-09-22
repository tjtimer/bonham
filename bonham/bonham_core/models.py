from datetime import datetime

import arrow
import asyncpg
import sqlalchemy as sa
import sqlamp
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy_utils import ArrowType, ChoiceType

from bonham.bonham_core import db
from bonham.bonham_core.b_types import PrivacyType
from bonham.bonham_core.helper import snake_case

__all__ = ('Base', 'BaseModel', 'Model')

Base = declarative_base(metaclass=sqlamp.DeclarativeMeta)


class BaseModel(object):
    """
        Parent class Models.

        Usage:
            Model definition:
                class MyModel(BaseModel, Base):
                    # column declaration
                    ...

                    def __init__(self, connection, **kwargs):
                        super().__init__(connection, **kwargs)
                        ...

            creating:
                model = MyModel(connection, **data)
                await model.create()

            updating an existing entry:
                entry = MyModel(connection [, **data])
                await entry.update(data=dict(data) [, ref=<str: column_name>])

                'ref' is optional and defaults to 'id'

        Models inheriting from BaseModel will have

            following columns:
                id

            following methods:
                create, update, delete,
                get, get_by_id
    """
    required_fields = set()
    read_only_fields = {
        'id', 'created', 'last_updated', 'update_count'
        }
    public_data = {
        'id', 'created', 'last_updated',
        'update_count', 'privacy'
        }

    @declared_attr
    def __tablename__(cls):
        return snake_case(cls.__name__)

    id = sa.Column(sa.Integer,
                   index=True, primary_key=True,
                   autoincrement=True, unique=True
                   )

    @declared_attr
    def privacy(self):
        return sa.Column(ChoiceType(PrivacyType, impl=sa.Integer()),
                         server_default='7')  # default is private

    def __init__(self, connection: asyncpg.Connection, **kwargs):
        assert isinstance(
            connection, asyncpg.Connection
            ), 'connection must be provided and ' \
               'of type asyncpg.Connection'
        assert all(key in self.__table__.c.keys() for key in kwargs.keys())
        self.connection = connection
        vars(self).update(
            {
                key: value for key, value in kwargs.items()
                if key in self.columns and value is not None
                }
            )

    def __str__(self):
        return f"<{self.__class__.__name__}: {vars(self)}>"

    def __repr__(self):
        return f"<{self.__class__.__name__}: {vars(self)}>"

    def __getitem__(self, name):
        if isinstance(vars(self)[name], datetime):
            value = arrow.get(vars(self)[name]).for_json()
            return value
        return vars(self)[name]

    @property
    def table(self):
        return self.__table__

    @property
    def columns(self):
        return self.__table__.c.keys()

    async def create(self, *, data=None, **kwargs):
        assert self.id is None, 'id must be None!'
        if data is None:
            data = {key: value for key, value in vars(self).items()
                    if key in self.columns and value is not None
                    }
        print(f"{self.table} create:\n\tdata: {data}\nkwargs: {kwargs}")
        result = await db.create(self.connection, self.table, data=data,
                                 **kwargs)
        vars(self).update(**dict(result))

    async def update(self, *, data=None, **kwargs):
        assert isinstance(data, dict), 'data must be provided and type dict'
        if kwargs.get('ref', None) is None:
            kwargs['ref'] = ('id', self.id)
        result = await db.update(self.connection, self.table, data=data,
                                 **kwargs)
        vars(self).update(**dict(result))

    async def delete(self, **kwargs):
        o_id = kwargs.pop('o_id', self.id)
        if o_id is None:
            raise TypeError(
                f"kwargs.pop('o_id', self.id) must not return None. "
                f"You have to set one of them!"
                )
        await db.delete(self.connection, self.table, o_id=o_id)
        del self

    async def get(self, **kwargs):
        where = kwargs.pop('where', f"id={self.id}")
        result = await db.get(
            self.connection, self.table,
            where=where, **kwargs
            )
        if result is None:
            return None
        if kwargs.pop('many', False):
            return (dict(row) for row in result)
        return vars(self).update(**dict(result))

    async def get_by_id(self, **kwargs):
        o_id = kwargs.pop('o_id', self.id)
        if o_id is None:
            raise TypeError(f"kwargs.pop('o_id', self._id) must not return "
                            f"None. You have to set one of them!")
        result = await db.get_by_id(self.connection, self.table, o_id=o_id,
                                    **kwargs)
        if result is None:
            return None
        vars(self).update(**dict(result))
        return self


class Model(BaseModel):
    """
        Parent class Models.

        Usage:
            Model definition:
                class MyModel(Model, Base):
                    # column declaration
                    ...

                    def __init__(self, connection, **kwargs):
                        super().__init__(connection, **kwargs)
                        ...

            creating:
                model = MyModel(connection, **data)
                await model.create()

            updating an existing entry:
                entry = MyModel(connection [, **data])
                await entry.update(data=dict(data) [, ref=<str: column_name>])

                'ref' is optional and defaults to ('id',)

        Models inheriting from Model will have

            following columns:
                id, privacy, created, last_updated

            following methods:
                create, update, delete,
                get, get_by_id
    """
    required_fields = set()
    read_only_fields = {
        'id', 'created', 'last_updated', 'update_count'
        }
    public_data = {
        'id', 'created', 'last_updated',
        'update_count', 'privacy'
        }

    @declared_attr
    def __tablename__(cls):
        return snake_case(cls.__name__)

    id = sa.Column(sa.Integer,
                   index=True, primary_key=True,
                   autoincrement=True, unique=True
                   )

    @declared_attr
    def privacy(self):
        return sa.Column(ChoiceType(PrivacyType, impl=sa.Integer()),
                         server_default='7')  # default is private

    @declared_attr
    def created(self):
        return sa.Column(
            ArrowType(timezone=True),
            server_default=sa.func.current_timestamp())

    @declared_attr
    def last_updated(self):
        return sa.Column(ArrowType(timezone=True),
                         nullable=True,
                         server_onupdate=sa.func.current_timestamp())

    @declared_attr
    def update_count(self):
        return sa.Column(sa.Integer, server_default='0')

    @declared_attr
    def disabled(self):
        return sa.Column(ArrowType)

    def __init__(self, connection: asyncpg.Connection, **kwargs):
        super().__init__(connection, **kwargs)


class Content(BaseModel):
    allows_comments = sa.Column(sa.Boolean, server_default="1")
    allows_likes = sa.Column(sa.Boolean, server_default="1")
