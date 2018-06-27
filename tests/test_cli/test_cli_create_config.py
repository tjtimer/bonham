# bonham test_cli_create_config
# created: 27.06.18
# Author: Tim "tjtimer" Jedro
# Email: tjtimer@gmail.com
import hypothesis.strategies as st
import pytest
from hypothesis import given

import bonham.cli.create_config as cc


@given(val=st.sampled_from(['0.0.1.dev', '3.5.1rc2', '1.0.3.dev4576', '0.2.1alpha2', '0.2.1.beta42']))
def test_get_version_valid(val):
    cc.input = lambda _: val
    result = cc.get_version()
    assert result == val


def test_get_version_invalid():
    cc.input = lambda _: 'A.0dev'
    with pytest.raises(ValueError) as e:
        cc.get_version()
    assert e.exconly() == ("ValueError: A.0dev is not a valid version declaration."
                           " (e.g. 0.0.1.dev, 0.1.2a2 etc.)")


def test_get_title_valid():
    cc.input = lambda _: 'My App Title'
    result = cc.get_title()
    assert result == 'My App Title'
