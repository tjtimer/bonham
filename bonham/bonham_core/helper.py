import asyncio
import random
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import uvloop
import yaml

__all__ = (
    'BLoop',
    'load_yaml_conf',
    'normalize_title',
    'camel_case',
    'kebap_case',
    'snake_case',
    'random_rgb'
    )


class BLoop(uvloop.Loop):
    r"""BLoop
    implementation of a custom event loop.
    """

    def __init__(self, *, debug: bool = False, **kwargs):
        super().__init__()
        print(f"BLoop self: {self}")
        self.set_debug(debug)

        executor = kwargs.pop(
            'executor', ProcessPoolExecutor
            )
        self.set_default_executor(executor)

        exception_handler = kwargs.pop(
            'exception_handler', self.exception_handler
            )
        self.set_exception_handler(exception_handler)

        asyncio.set_event_loop(self)

    def cancel_running_tasks(self):
        for task in asyncio.Task.all_tasks():
            print(f"task: {task} {task._state}")
            if task._state != 'FINISHED':
                task.cancel()

    def exception_handler(self,
                          _, context: dict
                          ) -> None:
        self.cancel_running_tasks()
        self.stop()

    def keyboardinterrupt_handler(self, *args):
        print(f"keyboardinterrupt_handler called.")
        print(f"self: {self}")
        print(f"args: {args}")
        self.run_until_complete(self.shutdown_asyncgens())

def load_yaml_conf(path: Path) -> dict:
    with open(path, 'r') as f:
        config = yaml.safe_load(f.read())
    return config


def normalize_title(value: str) -> str:
    return ' '.join(part.capitalize() for part in value.split(' '))


async def camel_case(value: str) -> str:
    v_list = value.replace('-', '_').split('_')
    camel_cased = v_list[0].lower()
    if len(camel_cased) == 1:
        return camel_cased
    camel_cased += ''.join(part.capitalize() for part in v_list[1:])
    return camel_cased


async def kebap_case(word: str) -> str:
    kebap_cased = word[0].lower()
    for letter in word[1:]:
        replacement = ''
        if ord(letter) in range(65, 91):  #
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


async def random_rgb() -> str:
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f"rgb({r}, {g}, {b})"
