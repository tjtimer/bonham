import asyncio
import random

import uvloop

__all__ = [
    "prepared_uvloop",
    ]


def prepared_uvloop(*, loop=None, debug=None):
    if loop is None or loop.is_closed():
        loop = uvloop.new_event_loop()
        asyncio.set_event_loop(loop)
    if debug:
        loop.set_debug(True)
    return loop


async def normalize_title(value):
    ' '.join(part.capitalize() for part in value.split(' '))


async def random_rgb():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f"rgb({r}, {g}, {b})"
