import arrow
import asyncpg
import hypothesis.strategies as st
import pytest
import random
from datetime import timedelta
from hypothesis import given
from sqlalchemy.exc import IntegrityError

from bonham.constants import PrivacyStatus
from bonham.db import create_tables
from bonham.settings import DSN


# TODO integrate hypothesis


def test_basemodel(testmodel):
    assert hasattr(testmodel, 'id')
    assert hasattr(testmodel, 'created')
    assert hasattr(testmodel, 'last_updated')
    assert hasattr(testmodel, 'privacy')
    assert hasattr(testmodel, 'create')
    assert hasattr(testmodel, 'get')
    assert hasattr(testmodel, 'update')
    assert hasattr(testmodel, 'delete')


def test_create_tables(testmodel):
    model = create_tables(models=[testmodel])[0]
    assert 'MetaData' == type(model.metadata).__name__
    assert 'testmodel' in model.metadata.tables.keys()


@pytest.mark.asyncio
async def test_model_create(testmodel):
    model = testmodel()
    async with asyncpg.create_pool(dsn=DSN) as pool:
        async with pool.acquire() as connection:
            await model.create(connection)
            assert model.last_updated is None
            assert model.id >= 1
            assert timedelta(seconds=0) <= (arrow.utcnow() - arrow.get(model.created)) <= timedelta(seconds=1)


@pytest.mark.asyncio
async def test_model_create_performance(testmodel):
    i = 0
    async with asyncpg.create_pool(dsn=DSN) as pool:
        async with pool.acquire() as connection:
            start = arrow.utcnow()
            while True:
                if i >= 1000:
                    break
                await testmodel().create(connection)
                i += 1
            end = arrow.utcnow()
    assert (end - start) <= timedelta(seconds=15)


@pytest.mark.asyncio
async def test_model_get(testmodel, _id):
    model = testmodel(id=_id)
    async with asyncpg.create_pool(dsn=DSN) as pool:
        async with pool.acquire() as connection:
            models = await model.get(connection, where=f"id={_id}")
            assert type(models).__name__ == 'generator'
            _list = list(models)
            if len(_list) > 0:
                assert arrow.get(_list[0]['created']) <= arrow.utcnow()


@pytest.mark.asyncio
async def test_model_get_with_kwargs(testmodel):
    model = testmodel()
    fields = 'id,privacy,last_updated'
    where = f"last_updated IS NOT NULL AND privacy IN (1, 2, 3, 4)"
    order_by = 'last_updated'
    limit = random.randint(1, 50)
    offset = 0
    offset2 = offset + limit
    async with asyncpg.create_pool(dsn=DSN) as pool:
        async with pool.acquire() as connection:
            models_page1 = await model.get(connection, fields=fields, where=where, limit=limit, order_by=order_by,
                                           offset=offset)
            models_page2 = await model.get(connection, fields=fields, where=where, limit=limit, order_by=order_by,
                                           offset=offset2)
            assert all(type(result).__name__ == 'generator' for result in [models_page1, models_page2])
            page1 = list(models_page1)
            page2 = list(models_page2)
            both = page1 + page2
            assert len(page1) <= limit
            assert len(page2) <= limit
            if len(page1) > 0:
                assert all(type(item).__name__ == 'dict' for item in both)
                assert all(item['privacy'] <= 4 for item in both)
                assert all('created' not in item.keys() for item in both)
                assert len(list({ model['id']: model for model in both })) is len(both)
                if len(page2) > 0:
                    assert arrow.get(page1[-1]['last_updated']) <= arrow.get(page2[0]['last_updated'])


@given(id=st.integers(min_value=1, max_value=20000), privacy=st.integers(min_value=1, max_value=7))
def test_model_update(my_loop, testmodel, id, privacy):
    async def _test_model_update():
        model = testmodel(id=id, privacy=PrivacyStatus(privacy))
        async with asyncpg.create_pool(dsn=DSN) as pool:
            async with pool.acquire() as connection:
                exists = len(list(await model.get(connection, where=f"id={id}")))
                if exists > 0:
                    await model.update(connection)
                    assert timedelta(seconds=0) <= (arrow.utcnow() - arrow.get(model.last_updated)) <= timedelta(
                        seconds=5)
                    assert model.privacy == privacy
                else:
                    with pytest.raises(IntegrityError) as ex_info:
                        await model.update(connection)
                    assert f"Update testmodel error. Record with id = {id} not found." in str(ex_info.value)

    my_loop.run_until_complete(_test_model_update())


@given(id=st.integers(min_value=1, max_value=20000))
def test_model_delete(my_loop, testmodel, id):
    async def _test_model_delete():
        model = testmodel(id=id)
        async with asyncpg.create_pool(dsn=DSN) as pool:
            async with pool.acquire() as connection:
                await model.delete(connection)
                del_model = await model.get(connection, where=f"id={id}")
                assert len(list(del_model)) == 0

    my_loop.run_until_complete(_test_model_delete())


@given(id=st.integers(min_value=1, max_value=20000), privacy=st.integers(min_value=1, max_value=7),
       hours=st.integers(min_value=1, max_value=1000))
def test_clean_data(my_loop, testmodel, id, privacy, hours):
    async def _test_clean_data():
        model = testmodel(id=id, privacy=privacy)
        model.created = created = arrow.utcnow().replace(hours=-hours)
        model.last_updated = last_updated = arrow.utcnow()
        clean_data = await model.clean_data()
        assert created.humanize() in clean_data['created']
        assert last_updated.humanize() in clean_data['last_updated']
        assert PrivacyStatus(privacy).label in clean_data['privacy']

    my_loop.run_until_complete(_test_clean_data())


@given(id=st.integers(min_value=1, max_value=20000), privacy=st.integers(min_value=1, max_value=7),
       hours=st.integers(min_value=1, max_value=1000))
def test_serialized(my_loop, testmodel, id, privacy, hours):
    async def _test_serialized():
        model = testmodel(id=id, privacy=privacy)
        model.created = created = arrow.utcnow().replace(hours=-hours)
        model.last_updated = last_updated = arrow.utcnow()
        serialized_data = await model.serialized()
        assert type(serialized_data).__name__ == 'dict'
        assert created.humanize() in serialized_data['created']
        assert last_updated.humanize() in serialized_data['last_updated']
        assert PrivacyStatus(privacy).label in serialized_data['privacy']

    my_loop.run_until_complete(_test_serialized())
