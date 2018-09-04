import sys

from bonham.app import app


def run():
    app.run(host='127.0.0.1', port=10667)


if __name__ == '__main__':
    print(sys.argv)
    run()
