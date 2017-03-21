import hypothesis.strategies as st
from hypothesis import given

from bonham.bonham_authentication.tests.helper import name_alphabet
from bonham.bonham_authentication.token import Token


@given(user_id=st.integers(min_value=1), user_name=st.text(alphabet=name_alphabet, min_size=3, max_size=20))
def test_token(my_loop, user_id, user_name):
    async def _test_token():
        payload = {
            'id': user_id,
            'email': '{}@email.com'.format(user_name.lower())
        }
        token = Token(loop=my_loop)
        encoded = await token.create(payload=payload)
        assert len(encoded.split(b'.')) == 3
        decoded = await token.verify_token(token=encoded)
        assert decoded['id'] == payload['id']

    my_loop.run_until_complete(_test_token())
