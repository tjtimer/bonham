import json

from hypothesis import given
import hypothesis.strategies as st
import requests

tables = ['account', 'accesstoken', 'calendar']

alphabet = st.text(st.characters(
        max_codepoint=1000,
        blacklist_categories=('Cc', 'Cs')),
        min_size=1
        ).map(lambda s: s.strip()).filter(lambda s: len(s) > 0)


@given(name=st.text(alphabet=alphabet, min_size=3, max_size=70))
def test_create_tag(name):
    name.replace('/', '')
    response = requests.post('https://tjtimer.dev/tags/', data=json.dumps(dict(name=name)), verify=False)
    assert response.status_code in [200, 400]


def test_get_tags():
    response = requests.get('https://tjtimer.dev/tags/', verify=False)
    assert response.status_code in [200, 400]


@given(table=st.sampled_from(tables),
       object_id=st.integers(min_value=1, max_value=10000))
def test_create_tagged_item(table, object_id):
    tags = requests.get('https://tjtimer.dev/tags/', verify=False)
    for tag in json.loads(tags.content)['tags']:
        print()
        print(f"tag name:")
        print(f"\t{tag['name']}")
        response = requests.post(f"https://tjtimer.dev/tags/{tag['name']}/",
                                 data=json.dumps(dict(table=table, object_id=object_id)),
                                 verify=False)
        # assert response.status_code in [200, 400]
        assert b'tagged_item' in response.content
