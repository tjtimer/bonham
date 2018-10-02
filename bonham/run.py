import sys
from pprint import pprint

from bonham.app import app


def run():
    pprint(vars(app))
    app.run(host='localhost', port=10667)


if __name__ == '__main__':
    run()
