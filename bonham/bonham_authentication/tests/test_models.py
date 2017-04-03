from hypothesis import strategies as st

from bonham.bonham_authentication.models import Account

alphabet = st.text(st.characters(
        max_codepoint=1000,
        blacklist_categories=('Cc', 'Cs')),
        min_size=1
        ).map(lambda s: s.strip()).filter(lambda s: len(s) > 0)


def test_account_model():
    assert all([hasattr(Account, key) for key in [
        'email',
        'password',
        'activation_key',
        'disabled',
        'logged_in',
        'is_superuser'
        ]])
