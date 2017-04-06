from datetime import timedelta
import random

import arrow
import asyncpg
from hypothesis import given
import hypothesis.strategies as st
import pytest

from bonham import db
from bonham.constants import PrivacyStatus
from bonham.db import BaseModel, Connect
from bonham.settings import DSN


def test_basemodel(testmodel):
    assert hasattr(testmodel, 'id')
    assert hasattr(testmodel, 'created')
    assert hasattr(testmodel, 'last_updated')
    assert hasattr(testmodel, 'privacy')


def test_create_tables(testmodel):
    model = db.create_tables(models=[testmodel])[0]
    assert 'testmodel' in model.metadata.tables.keys()
    for table in model.metadata.sorted_tables:
        print()
        print("table")
        print(table.c.keys())
        assert isinstance(table, (BaseModel, Connect))


@given(privacy=st.integers(min_value=1, max_value=7))
def test_create(my_loop, testmodel, privacy):
    async def _test_create():
        async with asyncpg.create_pool(dsn=DSN) as pool:
            async with pool.acquire() as connection:
                model = await testmodel().create(connection, data=dict(privacy=privacy))
                assert model['last_updated'] is None
                assert model['id'] >= 1
                assert timedelta(seconds=0) <= (arrow.utcnow() - arrow.get(model['created'])) <= timedelta(seconds=1)

    my_loop.run_until_complete(_test_create())


@given(id=st.integers(min_value=1, max_value=20000))
def test_get(my_loop, testmodel):
    async def _test_get():
        table = testmodel.__table__
        async with asyncpg.create_pool(dsn=DSN) as pool:
            async with pool.acquire() as connection:
                models = await testmodel().get(connection, table=table)
                print(f"Model Type generator: {type(models)}")
                assert type(models).__name__ == 'generator'
                _list = list(models)
                if len(_list) > 0:
                    assert arrow.get(_list[0]['created']) <= arrow.utcnow()

    my_loop.run_until_complete(_test_get())


@given(id=st.integers(min_value=1, max_value=20000))
def test_get_by_id(my_loop, testmodel, id):
    async def _test_get_by_id():
        async with asyncpg.create_pool(dsn=DSN) as pool:
            async with pool.acquire() as connection:
                model = await testmodel().get_by_id(connection, object_id=id)
                if model:
                    assert isinstance(model, (dict,))
                    assert arrow.get(model['created']) <= arrow.utcnow()
                else:
                    assert model is None

    my_loop.run_until_complete(_test_get_by_id())


def test_get_with_kwargs(my_loop, testmodel):
    async def _test_get_with_kwargs():
        table = testmodel.__table__
        fields = 'id,privacy,last_updated'
        where = f"last_updated IS NOT NULL AND privacy IN (1, 2, 3, 4)"
        order_by = 'last_updated'
        limit = random.randint(1, 50)
        offset = 0
        offset2 = offset + limit
        async with asyncpg.create_pool(dsn=DSN) as pool:
            async with pool.acquire() as connection:
                models_page1 = await testmodel().get(connection,
                                                     table=table,
                                                     fields=fields,
                                                     where=where,
                                                     limit=limit,
                                                     order_by=order_by,
                                                     offset=offset)
                models_page2 = await testmodel().get(connection,
                                                     table=table,
                                                     fields=fields,
                                                     where=where,
                                                     limit=limit,
                                                     order_by=order_by,
                                                     offset=offset2)
                assert all(type(result).__name__ == 'generator' for result in [models_page1, models_page2])
                page1 = list(models_page1)
                page2 = list(models_page2)
                both = page1 + page2
                assert len(page1) <= limit
                assert len(page2) <= limit
                if len(page1) > 0:
                    assert all(isinstance(item, (dict,)) for item in both)
                    assert all(item['privacy'] <= 4 for item in both)
                    assert all('created' not in item.keys() for item in both)
                    assert len(list({model['id']: model for model in both})) is len(both)
                    if len(page2) > 0:
                        assert arrow.get(page1[-1]['last_updated']) <= arrow.get(page2[0]['last_updated'])

    my_loop.run_until_complete(_test_get_with_kwargs())


@given(id=st.integers(min_value=1, max_value=20000), privacy=st.integers(min_value=1, max_value=7))
def test_update(my_loop, testmodel, id, privacy):
    async def _test_update():
        async with asyncpg.create_pool(dsn=DSN) as pool:
            async with pool.acquire() as connection:
                exists = await testmodel().get_by_id(connection, object_id=id)
                data = dict(id=id, privacy=PrivacyStatus(privacy))
                if exists:
                    model = await testmodel().update(connection, data=data)
                    assert timedelta(seconds=0) <= (arrow.utcnow() - arrow.get(model['last_updated'])) <= timedelta(
                        seconds=5)
                    assert model['privacy'] == privacy
                else:
                    with pytest.raises(TypeError) as ex_info:
                        await testmodel().update(connection, data=data)
                    assert f"Update testmodel error. Record with id = {id} not found." in str(ex_info.value)

    my_loop.run_until_complete(_test_update())


@given(id=st.integers(min_value=1, max_value=20000))
def test_delete(my_loop, testmodel, id):
    async def _test_delete():
        async with asyncpg.create_pool(dsn=DSN) as pool:
            async with pool.acquire() as connection:
                if await testmodel().delete(connection, object_id=id):
                    del_model = await testmodel().get_by_id(connection, object_id=id)
                    assert del_model is None

    my_loop.run_until_complete(_test_delete())
