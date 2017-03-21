from unittest import TestCase

import asyncpg
import pytest
from hypothesis import example, given, strategies as st

from bonham.bonham_authentication.models import Account, valid_email, valid_password, validate_data
from bonham.utils import prepared_uvloop
from settings import DSN

upper = [chr(n) for n in range(65, 90)]
lower = [chr(n) for n in range(97, 122)]
alphabet = upper + lower


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
            'locked',
            'logged_in',
            'privacy',
            'created',
            'last_updated',
            'create',
            'get',
            'update',
            'delete',
            ]])

    @given(name=st.text(alphabet=alphabet, min_size=3, max_size=20),
           email_host=st.text(alphabet=alphabet, min_size=3, max_size=9),
           email_ending=st.text(alphabet=alphabet, min_size=2, max_size=10),
           password=st.sampled_from(['#123Ta', '#123Ta?r', '123456789', '1728?umpaLUMPA!', ' 789Ab#?']))
    @example(name='Klaus', email_host='email', email_ending='com', password='#123Klaus')
    def test_account_create(self, name, email_host, email_ending, password):
        async def create_account():
            email = f"{name}@{email_host}.{email_ending}"
            if await valid_email(value=email) and await valid_password(value=password):
                account = Account(email=email, password=password)
                print(f"account: {vars(account)}")
                async with self.pool.acquire() as connection:
                    exists = len(list(await account.get(connection=connection, where=f"email='{email}'")))
                    if not exists:
                        await account.create(connection=connection)
                        print(f"created: {vars(account)}")
                        assert account.id >= 1
                    else:
                        with pytest.raises(asyncpg.UniqueViolationError) as ex_info:
                            await account.create(connection=connection)
                            assert f"account with email {email} already exists." in ex_info
            else:
                with pytest.raises(ValueError) as ex_info:
                    valid_data = {key: value async for key, value in validate_data(
                            data={
                                'email'   : email,
                                'password': password
                                }
                            )}
                    print(f"INVALID -> {ex_info.value}")
                    assert 'invalid!' in ex_info.value

        self.loop.run_until_complete(create_account())
