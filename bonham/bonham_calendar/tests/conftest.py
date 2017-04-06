import json

import pytest
import requests

from bonham.local_settings import LOCAL_ADMIN


@pytest.fixture
def admin_token():
    login_data = json.dumps({
        'email': LOCAL_ADMIN   ['email'],
        'password': LOCAL_ADMIN['password']
        })
    login = requests.put('https://tjtimer.dev/auth/login/', data=login_data, verify=False)
    token = login.headers.get('auth-token')
    return token


@pytest.fixture
def token():
    user_data = json.dumps({
        'email':    'klaus@email.com',
        'password': '#123Klaus'
        })
    response = requests.put('https://tjtimer.dev/auth/login/', data=user_data, verify=False)
    if response.status_code is not 200:
        response = requests.post('https://tjtimer.dev/auth/sign-up/', data=user_data, verify=False)
    _token = response.headers.get('auth-token')
    return _token
