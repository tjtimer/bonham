import json

from hypothesis import example, given
import hypothesis.strategies as st
import requests

alphabet = st.text(st.characters(
        max_codepoint=1000,
        blacklist_categories=('Cc', 'Cs')),
        min_size=1
        ).map(lambda s: s.strip()).filter(lambda s: len(s) > 0)


@given(name=st.text(alphabet=alphabet, min_size=3, max_size=20),
       password=st.text(alphabet=alphabet, min_size=6))
@example(name='Klaus', password='#123Klaus')
def test_sign_up(name, password):
    email = f"{name.lower()}@email.com"
    data = json.dumps({
        'email': email,
        'password': str(password)
        })
    response = requests.post('https://tjtimer.dev/auth/sign-up/', data=data, verify=False)
    assert response.status_code in [200, 400]
    if response.status_code == 400:
        error_messages = [f"account with email {email} already exists.",
                          "Invalid email and/or password!"]
        assert response.json()['error'] in error_messages
    else:
        assert 'Auth-Token' in response.headers.keys()
        assert len(response.headers.get('Auth-Token').split('.')) == 3


@given(name=st.text(alphabet=alphabet, min_size=3, max_size=20),
       password=st.text(alphabet=alphabet, min_size=6))
@example(name='Klaus', password='#123Klaus')
def test_login(name, password):
    email = f"{name.lower()}@email.com"
    data = json.dumps({
        'email':    email,
        'password': str(password)
        })
    response = requests.put('https://tjtimer.dev/auth/login/', data=data, verify=False)
    assert response.status_code in [200, 401]
    if response.status_code == 401:
        error_messages = [f"account with email {email} does not exist",
                          "wrong password!"]
        assert response.json()['error'] in error_messages
    else:
        assert 'Auth-Token' in response.headers.keys()
        assert len(response.headers.get('Auth-Token').split('.')) == 3
