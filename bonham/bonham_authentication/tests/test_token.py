import hypothesis.strategies as st
from hypothesis import given

from bonham.bonham_authentication import token
from bonham.bonham_authentication.tests.helper import async_test, name_alphabet


@given(user_id=st.integers(min_value=1), user_name=st.text(alphabet=name_alphabet, min_size=3, max_size=20))
@async_test
def test_token(user_id, user_name):
    user = {
        'id': user_id,
        'name': str(user_name),
        'email': '{}@email.com'.format(user_name.lower())
    }
    encoded = yield from token.create(user)
    assert len(encoded.split(b'.')) == 3
    decoded = yield from token.decode(encoded)
    assert decoded['id'] == user['id']


@given(user_id=st.integers(min_value=1), user_name=st.text(alphabet=name_alphabet, min_size=3, max_size=20))
def test_token_async(my_loop, user_id, user_name):
    async def _test_token():
        user = {
            'id': user_id,
            'name': str(user_name),
            'email': '{}@email.com'.format(user_name.lower())
        }
        encoded = await token.create(user)
        assert len(encoded.split(b'.')) == 3
        decoded = await token.decode(encoded)
        assert decoded['id'] == user['id']

    my_loop.run_until_complete(_test_token())
