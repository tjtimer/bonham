import hypothesis.strategies as st
from hypothesis import given

from bonham.bonham_authentication.tests.helper import async_test, name_alphabet
from bonham.bonham_authentication.token import Token


@given(user_id=st.integers(), user_name=st.text(alphabet=name_alphabet, min_size=3, max_size=20))
@async_test
def test_token(user_id, user_name):
    token = Token()
    user = {
        'id': user_id,
        'name': str(user_name),
        'email': '{}@email.com'.format(user_name.lower())
    }
    encoded = yield from token.create(user)
    assert len(encoded.split('.')) == 3
    decoded = yield from token.decode(encoded)
    assert decoded['id'] == user['id']
