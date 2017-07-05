import asyncio
import random
from collections import namedtuple
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import uvloop
import yaml

__all__ = [
    'prepared_uvloop', 'prepared_socket', 'load_yaml_conf',
    'normalize_title', 'camel_case', 'snake_case', 'random_rgb', 'route'
    ]


def load_yaml_conf(path: Path)-> dict:
    with open(path, 'r') as f:
        config = yaml.safe_load(f.read())
    return config


def prepared_uvloop(*, debug: bool=False, **kwargs):
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.set_debug(debug)
    return loop


async def cancel_tasks():
    for task in asyncio.Task.all_tasks():
        task.cancel()


def normalize_title(value: str) -> str:
    ' '.join(part.capitalize() for part in value.split(' '))


def camel_case(value: str) -> str:
    v_list = value.replace('-', '_').split('_')
    if len(v_list) == 1:
        return value.lower()
    camel_cased = v_list[0].lower()
    camel_cased += ''.join(part.capitalize() for part in v_list[1:])
    return camel_cased


def kebap_case(word: str) -> str:
    kebap_cased = word[0].lower()
    for letter in word[1:]:
        replacement = ''
        if ord(letter) in range(65, 91):
            replacement += f"-{letter.lower()}"
        kebap_cased += replacement
    return kebap_cased


def snake_case(word: str) -> str:
    snake_cased = word[0].lower()
    for letter in word[1:]:
        if ord(letter) in range(65, 91):
            letter = f"_{letter.lower()}"
        snake_cased += letter
    return snake_cased

async def async_snake_case(word: str) -> str:
    return snake_case(word)


async def random_rgb() -> str:
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f"rgb({r}, {g}, {b})"

channel = namedtuple('channel', ['topics', 'socket', 'subscribers'])
