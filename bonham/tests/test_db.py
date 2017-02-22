from datetime import timedelta

import arrow
import asyncpg
import pytest
import random
from sqlalchemy import and_

from bonham.constants import PrivacyStatus
from bonham.db import create_tables
from bonham.settings import DSN


def test_basemodel(testmodel):
    assert hasattr(testmodel, 'id')
    assert hasattr(testmodel, 'created')
    assert hasattr(testmodel, 'last_updated')
    assert hasattr(testmodel, 'privacy')


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
async def test_model_get(testmodel):
    async with asyncpg.create_pool(dsn=DSN) as pool:
        async with pool.acquire() as connection:
            models = await testmodel().get(connection, where=and_(testmodel.__table__.c.id == 1))
            assert type(models).__name__ == 'generator'
            assert arrow.get(list(models)[0]['created']) <= arrow.utcnow()


@pytest.mark.asyncio
async def test_model_update(testmodel):
    _id = random.randint(1, 5000)
    privacy = PrivacyStatus(random.randint(1, 7))
    model = testmodel(id=_id, privacy=privacy)
    async with asyncpg.create_pool(dsn=DSN) as pool:
        async with pool.acquire() as connection:
            await model.update(connection)
            assert timedelta(seconds=0) <= (arrow.utcnow() - arrow.get(model.last_updated)) <= timedelta(seconds=5)
            assert model.privacy == privacy.value
            assert PrivacyStatus(model.privacy) == privacy


@pytest.mark.asyncio
async def test_model_delete(testmodel):
    _id = random.randint(1, 5000)
    model = testmodel(id=_id)
    async with asyncpg.create_pool(dsn=DSN) as pool:
        async with pool.acquire() as connection:
            await model.delete(connection)
            del_model = await model.get(connection, where=and_(model.__table__.c.id == _id))
            assert len(list(del_model)) is 0
