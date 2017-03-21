import asyncio

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
