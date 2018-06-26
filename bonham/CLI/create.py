"""
create
"""
import asyncio
from getpass import getpass
from pathlib import Path

from bonham.core.ssl import create_priv_pub_keys


def run():
    coro = asyncio.sleep(1)
    loop = asyncio.get_event_loop()
    print("What shall be created?")
    print("1. a pair of private and public keys")
    print("2. nothing")
    what = int(input('[1|2]: '))
    if what == 1:
        print("Where should those key files be stored? (path to a directory)")
        path = Path(input()).resolve()
        print("What prefix should those file names get? (server or app or <my-app-name>)")
        name = input()
        print("please provide a password")
        pw = getpass()
        coro = create_priv_pub_keys(name, path=path, secret=pw)
    loop.run_until_complete(coro)
