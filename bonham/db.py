import logging
from typing import Any, Iterator

import asyncpg
import psycopg2 as psql
import sqlalchemy as sa
from aiohttp import web
from aiohttp.signals import Signal
from asyncpg.connection import Connection
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from bonham import BaseModel
from bonham.settings import DEVELOPMENT_MODE, DSN

__all__ = ['setup', 'shutdown', 'ForeignKey', 'create_db', 'drop_db', 'create_table', 'drop_table',
           'create', 'update', 'delete', 'get', 'get_by_id', 'get_by_key']

#  engine to use for table creation
engine = sa.create_engine(DSN, client_encoding='utf8')


def create_db(name: str, *, user: str=None, password: str=None) -> None:
    """
    Create a new database with given name
    :param name: name of database to create
    :param user: user name / database role
    :param password: database server password for given user / role
    :return: None or raise Exception
    """
    if user is None or password is None:
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


def drop_db(name: str, *, user: str=None, password: str=None) -> None:
    """
    Drop database with given name
    :param name: name of database to create
    :param user: user name / database role
    :param password: database server password for given user / role
    :return: None or raise Exception
    """
    if user is None or password is None:
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


async def setup(app: web.Application) -> web.Application:
    """
    Create a connection pool to a postgresql database and setup signals. Add this to given app.
    
    Usage:
        to get a connection as context manager
        async with app.db.acquire() as connection:
            result = await connection.execute(query)
        
        to listen to signals use any list methods, e.g. app.db.on_obj_created.append(my_listener_func)
        to send a signal use coroutine send, e.g. await app.db.on_obj_created.send(*args, **kwargs)
    :param app: application instance
    :return: updated application instance
    """
    db = await asyncpg.create_pool(dsn=DSN, loop=app.loop, command_timeout=60)
    db.tables = {}
    db.on_obj_created = Signal(app)
    db.on_obj_updated = Signal(app)
    db.on_obj_deleted = Signal(app)
    app.db = db
    return app

async def shutdown(app):
    await app.db.close()
    print(f"app db is closed.")
    return app

async def create_table(model: BaseModel) -> sa.Table:
    """
    Create a new table 
    :param model: a representation of the table to create (model attributes will be table columns) 
    :return: the newly created table as an instance of sqlalchemy table
    """
    model.__table__.create(engine, checkfirst=True)
    return model.__table__


async def drop_table(connection, table):
    if not DEVELOPMENT_MODE:
        return
    connection.execute(f"DROP TABLE {table} CASCADE")
    connection.close()


def ForeignKey(related: str, **kwargs) -> sa.Column:
    """
    Shortcut for sqlalchemy's ForeignKey.  
    :param related: table name of related object
    :param kwargs: contains config options of ForeignKey, like ondelete, onupdate (for both default is CASCADE)
                        or primary_key (default is True)
                         read postgresql documentation for more information
                         https://www.postgresql.org/docs/9.6/static/ddl-constraints.html#DDL-CONSTRAINTS-FK
    :return: Foreignkey definition
    """
    ondelete = kwargs.get('ondelete', "CASCADE")
    onupdate = kwargs.get('onupdate', "CASCADE")
    primary_key = kwargs.get('primary_key', True)
    return sa.Column(sa.Integer, sa.ForeignKey(f"{related}.id", ondelete=ondelete, onupdate=onupdate),
                     primary_key=primary_key)

async def create(connection, table: str, *, data: dict = None) -> dict or None:
    """
    Create a new row in given table.
    :param connection:  Connection to database
    :param table: table name
    :param data: key: value pairs where keys are column names and values the corresponding values
    :return: new row as a dict
    """
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

async def update(connection: Connection, table: str, *, data: dict = None, **kwargs) -> dict or None:
    """
    Update a single row in given table.
    :param connection:  Connection to database
    :param table: table name
    :param data: key: value pairs with data (must contain object id or reference key and value if kwargs['ref'] is given)
    :return: updated row as dict containing all columns or those specified by kwargs['return'] 
    """
    ref = kwargs.get('ref', 'id')
    ret = kwargs.get('return', '*')
    updates = ','.join(f"{key}={value} " for key, value in data.items()
                       if key not in [ref, 'id', 'created'] and value is not None)
    defaults = "last_updated=CURRENT_TIMESTAMP, update_count=update_count+1"
    stmt = f"UPDATE {table} SET {updates}, {defaults} WHERE {ref} = '{data[ref]}' RETURNING {','.join(ret)}"
    result = await connection.fetchrow(stmt)
    if result:
        return dict(result)
    else:
        return None

async def delete(connection, table: str, *, o_id: int = None) -> int or None:
    """
    Delete a single row from the given table.
    :param connection:  Connection to database
    :param table: table name
    :param o_id: id of object to delete
    :return: id of deleted object or None
    """
    stmt = f"DELETE FROM {table} WHERE id={o_id}"
    result = await connection.fetchval(stmt)
    if result:
        return result
    return None

async def get(connection: Connection, table: str, *, where: str = None, **kwargs) -> Iterator or None:
    """
    Get all rows that match the given parameters/filters.
    :param connection:  Connection to database
    :param table: table name
    :param where: filter string (e.g. "id=<some_id> AND name=<some_name>")
    :return: a generator with every row as dict containing all columns or those specified by kwargs['fields'] 
    :rtype: generator / Iterator
    """
    fields = kwargs.get('fields', '*')
    order_by = kwargs.get('order_by', 'id')
    offset = kwargs.get('offset', 0)
    limit = kwargs.get('limit', 100)
    stmt = f"SELECT {','.join(fields)} FROM {table} "
    if where is not None:
        stmt += f"WHERE {where} "
    stmt += f"ORDER BY {order_by} OFFSET {offset} LIMIT {limit}"
    rows = await connection.fetch(stmt)
    if len(rows):
        return (dict(row) for row in rows)
    return None

async def get_by_id(connection: Connection, table: str, *, o_id: int = None, **kwargs) -> dict or None:
    """
    Get a single row by given id.
    :param connection:  Connection to database
    :param table: table name
    :param o_id: id of object
    :return: the matching row as dict containing all columns or those specified by kwargs['fields'] 
    """
    fields = kwargs.get('fields', '*')
    stmt = f"SELECT {','.join(fields)} FROM {table} WHERE id={o_id}"
    row = await connection.fetchrow(stmt)
    if row:
        return dict(row)
    return None

async def get_by_key(connection: Connection, table: str, *,
                     key: str = None, value: Any = None, **kwargs) -> dict or Iterator or None:
    """
    Get row(s) by given key value pair.
    :param connection:  Connection to database
    :param table: table name
    :param key: name of referenced column
    :param value: value to search for
    :returns: if kwargs['many'] and kwargs['many'] is True this method returns an generator / Iterator
                    containing each matching row as a dict else returns a single matching row as dict
    """
    fields = kwargs.get('fields', '*')
    many = kwargs.get('many', False)
    operator = kwargs.get('operator', '=')
    stmt = f"SELECT {','.join(fields)} FROM {table} WHERE {key} {operator} '{value}'"
    if many:
        rows = await connection.fetch(stmt)
        if rows:
            return (dict(row) for row in rows)
        else:
            return None
    row = await connection.fetchrow(stmt)
    if row:
        return dict(row)
    return None
