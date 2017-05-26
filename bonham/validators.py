import re


__all__ = ['has_digits', 'has_no_digits', 'has_uppercase', 'has_no_uppercase', 'has_lowercase', 'has_no_lowercase',
           'has_specialchars', 'has_no_specialchars', 'has_whitespaces', 'has_no_whitespaces', 'is_longer_than',
           'is_shorter_than', 'is_valid_email', 'is_valid_rgb']

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

async def has_specialchars(value, *, chars=None):
    if chars is None:
        chars = SPECIAL_CHARS
    return re.search(chars, value) is not None

async def has_no_specialchars(value, *, chars=None):
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

async def is_valid_rgb(value: str) -> bool:
    is_rgb_string = re.search(r'^rgb\([0-9]{1,3}, [0-9]{1,3}, [0-9]{1,3}\)', value) is not None
    return is_rgb_string
