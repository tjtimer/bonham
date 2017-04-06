from hypothesis import strategies as st

from bonham.bonham_tag.models import Tag

alphabet = st.text(st.characters(
        max_codepoint=1000,
        blacklist_categories=('Cc', 'Cs')),
        min_size=1
        ).map(lambda s: s.strip()).filter(lambda s: len(s) > 0)


def test_tag_model():
    assert all([hasattr(Tag(), key) for key in [
        'tag'
        ]])
