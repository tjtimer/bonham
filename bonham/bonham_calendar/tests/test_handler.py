import json

from hypothesis import example, given
import hypothesis.strategies as st
import requests

alphabet = st.text(st.characters(
        max_codepoint=1000,
        blacklist_categories=('Cc', 'Cf', 'Cn', 'Co', 'Cs', 'Lm', 'Lo', 'So', 'Zl', 'Zp')),
        min_size=3,
        ).map(lambda s: s.strip()).filter(lambda s: len(s) > 0)


@given(cal_type=st.text(alphabet=alphabet),
       cal_title=st.text(alphabet=alphabet))
@example(cal_type="concert", cal_title="shows")
def test_create_unauthenticated(cal_type, cal_title):
    data = json.dumps(dict(
            type=cal_type,
            title=cal_title
            ))
    response = requests.post('https://tjtimer.dev/calendars/',
                             data=data,
                             verify=False)
    assert response.status_code == 401


@given(cal_type=st.text(alphabet=alphabet),
       cal_title=st.text(alphabet=alphabet))
@example(cal_type="concert", cal_title="shows")
def test_create_authenticated(cal_type, cal_title, admin_token):
    data = json.dumps(dict(
            type=cal_type,
            title=cal_title
            ))
    response = requests.post('https://tjtimer.dev/calendars/',
                             data=data,
                             headers={'AUTH-TOKEN': admin_token},
                             verify=False)
    assert response.status_code in [200, 400, 409]
    content = json.loads(response.content)
    if response.status_code != 200:
        assert 'error' in content.keys()
        if response.status_code == 400:
            assert 'You already have a calendar with that type and that title.' in content['error']
        if response.status_code == 409:
            assert 'invalid data' in content['error']
    else:
        assert 'calendar' in content.keys()
        assert all(key in content['calendar'].keys() for key in ['owner', 'type', 'title', 'color', 'show'])


def test_get_unauthenticated():
    response = requests.get('https://tjtimer.dev/calendars/',
                            verify=False)
    assert response.status_code in [200, 400, 409]
