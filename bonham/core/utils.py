import os
import random


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
