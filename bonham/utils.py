import asyncio
import random

import uvloop

__all__ = ['prepared_uvloop', 'normalize_title', 'camel_case', 'snake_case', 'random_rgb']


def prepared_uvloop(*, debug=None):
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    if debug:
        loop.set_debug(True)
    return loop


async def normalize_title(value):
    ' '.join(part.capitalize() for part in value.split(' '))


async def camel_case(value):
    v_list = value.replace('-', '_').split('_')
    if len(v_list) == 1:
        return value.lower()
    cc_value = v_list[0].lower()
    cc_value += ''.join(part.capitalize() for part in v_list[1:])
    return cc_value


def snake_case(value):
    n_value = value[0].lower()
    for letter in value[1:]:
        if ord(letter) in range(65, 91):
            letter = f"_{letter.lower()}"
        n_value += letter
    return n_value

async def async_snake_case(value):
    n_value = value[0].lower()
    for letter in value[1:]:
        if ord(letter) in range(65, 91):
            letter = f"_{letter.lower()}"
        n_value += letter
    return n_value


async def random_rgb():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f"rgb({r}, {g}, {b})"
