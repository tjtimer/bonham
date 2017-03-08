import asyncio
from concurrent.futures import ProcessPoolExecutor

import uvloop


def prepared_uvloop(*, loop=None, debug=None):
    if loop is None or loop.is_closed():
        loop = uvloop.new_event_loop()
        asyncio.set_event_loop(loop)
    if debug:
        loop.set_debug(True)
    loop.set_default_executor(ProcessPoolExecutor())
    return loop
