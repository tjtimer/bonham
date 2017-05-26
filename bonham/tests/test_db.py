import random
from collections import Iterator
from datetime import timedelta

import arrow
import asyncpg
import hypothesis.strategies as st
from aiohttp import web
from aiohttp.signals import Signal
from hypothesis import given
from sqlalchemy import Table

from bonham import db
from bonham.models import BaseModel, Connect
from bonham.settings import DSN
from bonham.utils import prepared_uvloop


def test_create_db():
    db = db.create_db('test_db', 'junge', 'baum')
    assert db


def test_setup_db():
    loop = prepared_uvloop()
    app = web.Application()
    loop.run_until_complete(db.setup(app))
    assert hasattr(app, 'db')
    assert isinstance(app.db, asyncpg.pool.Pool)
    assert hasattr(app, 'on_db_obj_created')
    assert isinstance(app.on_db_obj_created, Signal)
    assert hasattr(app, 'on_db_obj_updated')
    assert isinstance(app.on_db_obj_updated, Signal)
    assert hasattr(app, 'on_db_obj_deleted')
    assert isinstance(app.on_db_obj_deleted, Signal)


def test_create_tables(testmodel):
    models = db.create_tables(models=[testmodel])
    assert testmodel.__table__ in models
    for table in models:
        print()
        print("table")
        print(table.c.keys())
        assert isinstance(table, (BaseModel, Connect, Table))


@given(privacy=st.integers(min_value=1, max_value=7))
def test_create(testmodel, privacy, my_loop):
    async def _test_create():
        async with asyncpg.create_pool(dsn=DSN) as pool:
            async with pool.acquire() as connection:
                model = await testmodel().create(connection, data=dict(privacy=privacy))
                assert model['last_updated'] is None
                assert model['id'] >= 1
                now = arrow.utcnow()
                created = arrow.get(model['created']).to('utc')
                assert (now - created) <= timedelta(seconds=1)

    my_loop.run_until_complete(_test_create())


def test_get(testmodel, my_loop):
    async def _test_get():
        async with asyncpg.create_pool(dsn=DSN) as pool:
            async with pool.acquire() as connection:
                models = await testmodel().get(connection)
                if models:
                    assert type(models).__name__ == 'generator'
                    assert arrow.get(list(models)[0]['created']) <= arrow.utcnow()
    my_loop.run_until_complete(_test_get())


@given(id=st.integers(min_value=1, max_value=20000))
def test_get_by_id(testmodel, id, my_loop):
    async def _test_get_by_id():
        async with asyncpg.create_pool(dsn=DSN) as pool:
            async with pool.acquire() as connection:
                model = await testmodel().get_by_id(connection, o_id=id)
                if model:
                    assert isinstance(model, (dict,))
                    assert arrow.get(model['created']) <= arrow.utcnow()
                else:
                    assert model is None

    my_loop.run_until_complete(_test_get_by_id())


def test_get_with_kwargs(testmodel, my_loop):
    async def _test_get_with_kwargs():
        fields = 'id,privacy,last_updated'
        where = f"last_updated IS NOT NULL AND privacy IN (1, 2, 3, 4)"
        order_by = 'last_updated ASC'
        limit = random.randint(1, 50)
        offset = 0
        offset2 = offset + limit
        async with asyncpg.create_pool(dsn=DSN) as pool:
            async with pool.acquire() as connection:
                models_page1 = await testmodel().get(connection,
                                                     fields=fields,
                                                     where=where,
                                                     limit=limit,
                                                     order_by=order_by,
                                                     offset=offset)
                models_page2 = await testmodel().get(connection,
                                                     fields=fields,
                                                     where=where,
                                                     limit=limit,
                                                     order_by=order_by,
                                                     offset=offset2)
                assert all([isinstance(result, (Iterator,))
                            for result in [models_page1, models_page2] if result is not None])
                if models_page1:
                    page1 = list(models_page1)
                    assert len(page1) <= limit
                    assert all(isinstance(item, (dict,)) for item in page1)
                    assert all(item['privacy'] <= 4 for item in page1)
                    assert all('created' not in item.keys() for item in page1)
                    if models_page2:
                        page2 = list(models_page2)
                        assert len(page2) <= limit
                        assert arrow.get(page1[-1]['last_updated']) <= arrow.get(page2[0]['last_updated'])
                        both = page1 + page2
                        assert all(isinstance(item, (dict,)) for item in both)
                        assert all(item['privacy'] <= 4 for item in both)
                        assert all('created' not in item.keys() for item in both)
                        assert len(list({model['id']: model for model in both})) is len(both)

    my_loop.run_until_complete(_test_get_with_kwargs())


@given(id=st.integers(min_value=1, max_value=20000), privacy=st.integers(min_value=1, max_value=7))
def test_update(testmodel, id, privacy, my_loop):
    async def _test_update():
        async with asyncpg.create_pool(dsn=DSN) as pool:
            async with pool.acquire() as connection:
                exists = await testmodel().get_by_id(connection, id=id)
                data = dict(id=id, privacy=privacy)
                model = await testmodel().update(connection, data=data)
                if exists:
                    assert (arrow.utcnow() - arrow.get(model['last_updated']).to('utc')) <= timedelta(
                            seconds=5)
                    assert model['privacy'] == privacy
                else:
                    assert model is None

    my_loop.run_until_complete(_test_update())


@given(id=st.integers(min_value=1, max_value=20000))
def test_delete(testmodel, id, my_loop):
    async def _test_delete():
        async with asyncpg.create_pool(dsn=DSN) as pool:
            async with pool.acquire() as connection:
                if await testmodel().delete(connection, id=id):
                    del_model = await testmodel().get_by_id(connection, id=id)
                    assert del_model is None

    my_loop.run_until_complete(_test_delete())
