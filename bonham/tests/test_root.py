import requests

from bonham.settings import HOST, PORT


def test_app_index():
    index = requests.get(f'http://{HOST}:{PORT}/')
    assert index.status_code is 200
    assert b'Bonham' in index.content.title()
