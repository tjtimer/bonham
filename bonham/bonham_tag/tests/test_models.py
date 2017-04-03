from unittest import TestCase

import asyncpg
from hypothesis import example, given, strategies as st
import pytest

from bonham.bonham_authentication.models import Account, valid_email, valid_password, validate_data
from bonham.settings import DSN
from bonham.utils import prepared_uvloop

alphabet = st.text(st.characters(
        max_codepoint=1000,
        blacklist_categories=('Cc', 'Cs')),
        min_size=1
        ).map(lambda s: s.strip()).filter(lambda s: len(s) > 0)


class TestAccount(TestCase):
    def setUp(self):
        self.account = Account()
        self.loop = prepared_uvloop(debug=True)
        self.pool = self.loop.run_until_complete(asyncpg.create_pool(dsn=DSN, loop=self.loop, command_timeout=60))

    def tearDown(self):
        # drop_tables(tables=["account"])
        pass

    def test_account_model(self):
        assert all([hasattr(self.account, key) for key in [
            'id',
            'email',
            'password',
            'activation_key',
            'blocked',
            'logged_in',
            'privacy',
            'created',
            'last_updated',
            'create',
            'get',
            'update',
            'delete',
            ]])

    @given()
    @example()
    def test_account_create(self, name, email_host, email_ending, password):
        async def create_account():
            email = f"{name}@{email_host}.{email_ending}"
            if await valid_email(value=email) and await valid_password(value=password):
                account = Account(email=email, password=password)
                async with self.pool.acquire() as connection:
                    exists = len(list(await account.get(connection=connection, where=f"email='{email}'")))
                    if not exists:
                        await account.create(connection=connection)
                        assert account.id >= 1
                    else:
                        with pytest.raises(asyncpg.UniqueViolationError) as ex_info:
                            await account.create(connection=connection)
                            assert f"account with email {email} already exists." in ex_info
            else:
                with pytest.raises(ValueError) as ex_info:
                    data = {
                        'email':    email,
                        'password': password
                        }
                    async for _ in validate_data(data.items()):
                        pass
                    print(f"ex_info value: {ex_info.value}")
                    assert 'invalid!' in ex_info.value

        self.loop.run_until_complete(create_account())
