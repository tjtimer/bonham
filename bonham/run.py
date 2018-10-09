import asyncio
from pprint import pprint

from bonham.app import setup


def run():
    app = asyncio.get_event_loop().run_until_complete(setup())
    print('setup done!')
    pprint(vars(app))
    app.run(host='localhost', port=10667)


if __name__ == '__main__':
    run()
