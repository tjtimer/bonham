import hypothesis.strategies as st
from hypothesis import given

from bonham.bonham_auth.token import verify_token
from .helper import name_alphabet


@given(user_id=st.integers(min_value=1), user_name=st.text(alphabet=name_alphabet, min_size=3, max_size=20))
def test_token(my_loop, user_id, user_name):
    async def _test_token():
        request = {
            'account': {
                'id':    user_id,
                'email': "{user_name.lower()}@email.com"
                },
            }
        request['auth_token'] = await create(payload=request['account'])
        assert len(request['auth_token'].split('.')) == 3
        decoded = await verify_token(request=request)
        assert decoded['id'] == request['account']['id']

    my_loop.run_until_complete(_test_token())
