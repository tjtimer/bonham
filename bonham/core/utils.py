import os
import random
import sys
from pathlib import Path

import aiofiles

__all__ = (
    'opj',
    'capitalize_title',
    'camel_case',
    'kebab_case',
    'snake_case',
    'random_rgb'
    )

opj = os.path.join

def capitalize_title(text: str) -> str:
    return ' '.join(part.capitalize() for part in text.split(' '))


def camel_case(word: str) -> str:
    v_list = word.replace('-', '_').split('_')
    if len(v_list) == 1:
        return word.lower()
    camel_cased = v_list[0].lower()
    camel_cased += ''.join(part.capitalize() for part in v_list[1:])
    return camel_cased


def kebab_case(word: str) -> str:
    kebab_cased = word[0].lower()
    for letter in word[1:]:
        if ord(letter) in range(65, 91):  #
            letter = f"-{letter.lower()}"
        kebab_cased += letter
    return kebab_cased.replace('_', '-')


def snake_case(word: str) -> str:
    snake_cased = word[0].lower()
    for letter in word[1:]:
        if ord(letter) in range(65, 91):
            letter = f"_{letter.lower()}"
        snake_cased += letter
    return snake_cased.replace('-', '_')


async def random_rgb() -> str:
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f"rgb({r}, {g}, {b})"


def from_coro():
    return sys._getframe(2).f_code.co_flags & 0x380


class File:
    def __init__(self, name, *, path=None, async_ctx=True):
        self._name = name
        if path is None:
            path = os.getcwd()
        self._path = Path(path).resolve()
        self._async_ctx = async_ctx

    @property
    def path(self):
        return self._path.joinpath(self._name)

    async def _write_async(self, content, *, mode='', append=False):
        mode = f'w{mode}'
        if append is True:
            mode = f'a{mode}'
        async with aiofiles.open(self.path, f'w{mode}') as f:
            await f.write(content)

    async def _read_async(self, *, mode=''):
        async with aiofiles.open(self.path, f'r{mode}') as f:
            async for line in f:
                yield line

    def _write_sync(self, content, *, mode='', append=False):
        mode = f'w{mode}'
        if append is True:
            mode = f'a{mode}'
        with open(self.path, f'{mode}') as f:
            f.write(content)

    def _read_sync(self, *, mode=''):
        with open(self.path, f'r{mode}') as f:
            for line in f:
                yield line

    def write(self, content, *, mode=''):
        if self._async_ctx is True or from_coro() is True:
            return self._write_async(content, mode=mode)
        return self._write_sync(content, mode=mode)

    def read(self, *, mode=''):
        if self._async_ctx is True or from_coro() is True:
            return self._read_async(mode=mode)
        return self._read_sync(mode=mode)

    def __enter__(self):
        self._async_ctx = False
        return self

    def __exit__(self, *exc):
        return

    async def __aenter__(self):
        self._async_ctx = True
        return self

    async def __aexit__(self, *exc):
        return
