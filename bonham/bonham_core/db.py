# bonham/db.py
import logging
from collections import namedtuple
from typing import Generator, Iterator

import asyncpg
import psycopg2 as psql
import sqlalchemy as sa
from asyncpg.connection import Connection
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from bonham.bonham_core.component import Component
from bonham.bonham_core.models import Base
from bonham.settings import DEBUG, DSN

version = '0.0.1b1'

__all__ = (
    'Db', 'ForeignKey',
    'create_db', 'drop_db',
    'create_tables', 'drop_tables',
    'create', 'update', 'delete',
    'get', 'get_by_id', 'get_by_key'
    )

log = logging.getLogger(__name__)
#  engine to use for table creation
engine = sa.create_engine(DSN, client_encoding='utf8')



def create_db(name: str, *, user: str = None, password: str = None) -> None:
    r"""
    Create a new database with given name
    :param name: name of database to create
    :param user: user name / database role
    :param password: database server password for given user / role
    :return: None or raise Exception
    """
    if user is None or password is not None:
        raise TypeError("Missing required keyword arguments user and/or password")
    try:
        con = psql.connect(
                dbname='postgres',
                user=user, host='localhost',
                password=password
                )
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)  # <-- ADD THIS LINE
        cur = con.cursor()
        cur.execute(f"CREATE DATABASE {name}")
    except psql.ProgrammingError as e:
        log = logging.getLogger()
        log.warning(f"CREATE DATABASE ERROR: {e} ")
        raise


def drop_db(name: str, *, user: str = None, password: str = None) -> None:
    r"""
    Drop database with given name
    :param name: name of database to create
    :param user: user name / database role
    :param password: database server password for given user / role
    :return: None or raise Exception
    """
    if user is None or password is not None:
        raise TypeError("Missing required keyword arguments user and/or password")
    try:
        con = psql.connect(
                dbname='postgres',
                user=user, host='localhost',
                password=password
                )
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        cur.execute(f"DROP DATABASE {name}")
    except psql.OperationalError as e:
        log = logging.getLogger()
        log.warning(f"DROP DATABASE ERROR: {e} ")
        raise


signals = (
    'on_db_obj_created',
    'on_db_obj_read',
    'on_db_obj_updated',
    'on_db_obj_deleted'
    )


class Db(Component):
    r"""Db
    Provides a database connection pool,
    available tables and signals.
    """
    def __init__(self):
        super().__init__()
        self._pool = None
        self.tables = {}

    async def setup(self, service=None):
        r"""Create an asyncpg connection _pool to a postgresql database
            and setup signals.

        Usage:
            to get a connection as context manager
            async with service.dbc.acquire() as connection:
                result = await connection.execute(query)

            to listen to signals use any list methods,
            e.g. service.on_db_obj_created.append(my_listener_coro)

            to send a signal use coroutine send,
            e.g. await service.on_db_obj_created.send(*args, **kwargs)

        :param service: service instance
        """
        self._pool = await asyncpg.create_pool(dsn=DSN, command_timeout=60)
        await service.register_signals(signals)
        setattr(service, 'db', self._pool)

    async def shutdown(self, service):
        r"""Gracefully shutdown all open connections to the database,
        close the connection _pool and remove attribute 'db' from service
        instance."""
        await self.channel.close()
        await self._pool.close()
        service.__delattr__('db')


def create_tables(models: (Iterator, Generator)) -> dict:
    r"""
    Create tables in the database
    Usage:
        class MyServiceComponent(Component):
            def __init__(self):
                self.tables = create_tables([<MyModel1>, <MyModel2>, ....])

            ...
            async def setup(self, service):
                service.tables.update(self.tables)

    """
    for model in models:
        model.metadata.bind = engine
    Base.metadata.create_all()
    return {
        model.__tablename__: namedtuple(
            model.__tablename__, model.__table__.c.keys()
            ) for model in models
        }


def drop_tables(tables: (list, tuple)) -> bool:
    r"""
    Drop tables from the database.
    :param tables: a list or tuple of table names that should get dropped
    :return: True if succeeded False otherwise
    """
    if not DEBUG:  # we don't want to drop tables in production
        return False
    connection = engine.connect()
    try:
        for table in tables:
            connection.execute(f"DROP TABLE {table} CASCADE")
        connection.close()
        return True
    except Exception as e:
        print(f"drop tables exception: {type(e).__name__}: {e}")
        return False


class ForeignKey(sa.Column):
    r"""
    Shortcut for sqlalchemy's ForeignKey.
    """

    def __init__(self, related: str, **kwargs):
        r"""
        :param related: table name of related object
        :param kwargs: contains config options of ForeignKey, like ondelete,
            onupdate (for both default is CASCADE)
            or primary_key (default is True)

        read postgresql documentation for more information
        https://www.postgresql.org/docs/9.6/static/ddl-constraints.html#DDL
        -CONSTRAINTS-FK
        """
        ondelete = kwargs.get('ondelete', "CASCADE")
        onupdate = kwargs.get('onupdate', "CASCADE")
        primary_key = kwargs.get('primary_key', True)
        super().__init__(
            sa.Integer,
            sa.ForeignKey(
                f"{related}.id",
                ondelete=ondelete,
                onupdate=onupdate),
            primary_key=primary_key
            )


async def create(connection: Connection, table: str, *,
                 data: dict = None, **kwargs) -> dict or None:
    r"""
    Create a new row in given table and return that newly created row.
    Specify which fields/columns to return by setting keyword argument
    'returning' to a list of column names (default is ['*']).
    :param connection: a database connection
    :param table: the database table name
    :param data: key: value pairs where keys are column names and values the corresponding values
    :returns: newly created row as dict
    """
    data = {
        key: value for key, value in data.items()
        if value is not None
        }
    columns = ','.join(key for key in data.keys())
    values = tuple(data.values()) if len(data.values()) > 1 \
        else f"('{list(data.values())[0]}')"
    ret = kwargs.pop('returning', ['*'])
    if len(ret) > 1 and not isinstance(ret, (list, tuple)):
        raise TypeError(f"<returning> must be type list or tuple")
    stmt = f"INSERT INTO {table} ({columns}) " \
           f"VALUES {values} " \
           f"RETURNING {','.join(ret)}"
    print(stmt)
    result = await connection.fetchrow(stmt)

    if result is not None:
        return dict(result)
    return None


async def update(
    connection: Connection, table: str, *,
    data: dict = None, ref: tuple = None, **kwargs
    ) -> dict or None:
    r"""
    Update a single row in given table.
    :param connection: connection to database
    :param table: table name
    :param data: key value pairs with new data (must contain object id or
        reference key and value if kwargs['ref'] is given)
    :return: updated row as dict containing all columns or those specified by
        kwargs['returning']
    """
    ret = kwargs.get('returning', ['*'])

    if not isinstance(ret, (list, tuple)):
        raise TypeError(f"<returning> must be type list or tuple")
    if ref is None:
        raise TypeError('ref must be given and of type tuple(str: '
                        'column_name, any: value)')
    updates = ','.join(
        f"{key}='{value}' " for key, value in data.items()
        if key not in [
            'id', 'created', 'last_updated', 'update_count'
            ]
        and value is not None
        )

    defaults = "last_updated=CURRENT_TIMESTAMP, update_count=update_count+1"

    stmt = f"UPDATE {table} " \
           f"SET {updates}, {defaults} " \
           f"WHERE {ref[0]} = '{ref[1]}' " \
           f"RETURNING {','.join(ret)}"
    print(stmt)
    result = await connection.fetchrow(stmt)

    if result is not None:
        return dict(result)
    return None


async def delete(connection, table: str, *, o_id: int = None) -> int or None:
    r"""
    Delete a single row from the given table.
    :param connection:  Connection to database
    :param table: table name
    :param o_id: id of object to delete
    :return: id of deleted object or None
    """
    stmt = f"DELETE FROM {table} WHERE id={o_id}"
    result = await connection.fetchval(stmt)
    if result is not None:
        return dict(result)
    return None


async def get(connection: Connection, table: str, *, where: str = None,
              **kwargs) -> Generator or None:
    r"""
    Get all rows that match the given parameters/filters.
    :param connection:  Connection to database
    :param table: table name
    :param where: filter string (e.g. "id=<some_id> AND name=<some_name>")
    :return: a generator with every row as dict containing
            all columns or those specified by kwargs['fields']
    :rtype: Generator / Iterator
    """
    fields = kwargs.get('fields', ['*'])
    if len(fields) > 1 and not isinstance(fields, (list, tuple)):
        raise TypeError(f"<fields> must be type list or tuple")
    stmt = f"SELECT {','.join(fields)} FROM {table} "
    if where is not None:
        stmt += f"WHERE {where} "
    print(f"\n\nDB get statement: {stmt}\n\n")

    if kwargs.get('many', False):
        order_by = kwargs.get('order_by', 'id')
        offset = kwargs.get('offset', 0)
        limit = kwargs.get('limit', 100)
        stmt += f"ORDER BY {order_by} " \
                f"OFFSET {offset} " \
                f"LIMIT {limit}"
        rows = await connection.fetch(stmt)
        if rows is not None:
            return (row for row in rows)
    else:
        row = await connection.fetchrow(stmt)
        if row is not None:
            return row
    return None


async def get_by_id(connection: Connection, table: str, *, o_id: int = None, **kwargs) -> dict or None:
    r"""
    Get a single row by given id.
    :param connection:  Connection to database
    :param table: table name
    :param o_id: id of object
    :return: the matching row as dict containing all columns or those specified by kwargs['fields']
    """
    fields = kwargs.get('fields', '*')
    if len(fields) > 1 and not isinstance(fields, (list, tuple)):
        raise TypeError(f"<fields> must be type list or tuple")
    stmt = f"SELECT {','.join(fields)} FROM {table} WHERE id={o_id}"
    row = await connection.fetchrow(stmt)
    if row is not None:
        return dict(row)
    return None
