import re


__all__ = ['has_digits', 'has_no_digits', 'has_uppercase', 'has_no_uppercase', 'has_lowercase', 'has_no_lowercase',
           'has_special_chars', 'has_no_special_chars', 'has_whitespaces', 'has_no_whitespaces', 'is_longer_than',
           'is_shorter_than', 'is_valid_email', 'is_valid_color']

SPECIAL_CHARS = "[\[\]\'!*+?$%&/()#\\\]"


async def has_digits(value):
    return re.search("[0-9]", value) is not None

async def has_no_digits(value):
    return re.search("[0-9]", value) is None

async def has_uppercase(value):
    return re.search("[A-Z]", value) is not None

async def has_no_uppercase(value):
    return re.search("[A-Z]", value) is None

async def has_lowercase(value):
    return re.search("[a-z]", value) is not None

async def has_no_lowercase(value):
    return re.search("[a-z]", value) is None

async def has_special_chars(value, *, chars=None):
    if chars is None:
        chars = SPECIAL_CHARS
    return re.search(chars, value) is not None

async def has_no_special_chars(value, *, chars=None):
    if chars is None:
        chars = SPECIAL_CHARS
    return re.search(chars, value) is None

async def has_whitespaces(value):
    return re.search("\s", value) is not None

async def has_no_whitespaces(value):
    return re.search("\s", value) is None

async def is_longer_than(value, length):
    return len(value) >= length

async def is_shorter_than(value, length):
    return len(value) <= length

async def is_valid_email(value: str) -> bool:
    return False if re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", value) is None else True

async def is_valid_color(value: str) -> bool:
    rgb_re = r'^rgb\(([0-9]{1,2}\,\s|[0-1]{1}[0-9]{1}[0-9]?\,\s|2[0-5]{1,2}\,\s){2}' \
             r'([0-9]{1,2}\,|[0-1]{1}[0-9]{1}[0-9]?|2[0-5]{1,2})\)$'
    is_rgb_string = re.search(rgb_re, value) is not None
    is_hex_string = re.search(r'^#[0-9a-fA-F]{3,6}$', value) is not None
    return is_rgb_string or is_hex_string
