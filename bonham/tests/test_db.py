import arrow
import asyncpg
import pytest

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
    async with asyncpg.create_pool(dsn=DSN) as pool:
        async with pool.acquire() as connection:
            await testmodel.create(connection)
            assert testmodel.id >= 1
            assert arrow.get(testmodel.created) <= arrow.utcnow()
