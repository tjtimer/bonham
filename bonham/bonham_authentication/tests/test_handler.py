import json

import hypothesis.strategies as st
import requests
from hypothesis import example, given

from bonham.bonham_authentication.tests.helper import name_alphabet, password_alphabet


@given(name=st.text(alphabet=name_alphabet, min_size=3, max_size=20),
       password=st.text(alphabet=password_alphabet, min_size=6))
@example(name='Klaus', password='#123Klaus')
def test_sign_up(name, password, decode):
    name = str(name)
    email = '{}@email.com'.format(name.lower())
    data = json.dumps({
        'name': str(name),
        'email': email,
        'password': str(password)
    })
    response = requests.post('http://neumeusic.dev/auth/sign-up/', data=data)
    assert response.status_code in [200, 401]
    if response.status_code == 401:
        message = {
            'message': {
                'type': 'error',
                'message': 'username: {} or email: {} already exists'.format(name, email)
            }
        }
        assert message == response.json()
    else:
        assert 'Auth-Token' in response.headers.keys()
        assert len(response.headers.get('Auth-Token').split('.')) == 3
