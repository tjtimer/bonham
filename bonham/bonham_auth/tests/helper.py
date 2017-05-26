import asyncio

name_alphabet = [str(chr(pointer)) for pointer in range(65, 123) if pointer not in range(91, 94)]
password_alphabet = [str(chr(pointer)) for pointer in range(50, 150)]


def async_test(f):
    def wrapper(*args, **kwargs):
        print(args, kwargs)
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)

    return wrapper
