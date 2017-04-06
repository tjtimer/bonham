"""
Bonham Development Server
Author: Tim Jedro
Version: 0.0.1a1 curio based

"""
from argparse import ArgumentParser
import datetime
import logging
import os
from pathlib import Path

import arrow
import curio
from curio import subprocess

from bonham.bonham_development.settings import FUNCTION_CALL, JS_DIR, ROOT_DIR

log = logging.getLogger(__name__)
start_tests = curio.Event()


async def has_changed(file):
    return (arrow.now() - arrow.get(os.stat(file).st_mtime)) <= datetime.timedelta(seconds=1)


async def file_watcher(directory, pattern):
    try:
        print(f"file_watcher started!\nwatching: {directory} {pattern}\n")
        while True:
            await curio.sleep(1)
            f_changed = [file.name for file in Path(directory).glob(pattern) if await has_changed(file)]
            if len(f_changed) >= 1:
                return f_changed
    except curio.CancelledError:
        print(f"file watcher cancelled")
        raise


async def file_watchers(watch_js):
    print(f"starting file watchers")
    async with curio.TaskGroup(wait=any) as wg:
        try:
            await wg.spawn(file_watcher, ROOT_DIR, '**/*.py')
            if watch_js:
                wg.spawn(file_watcher, JS_DIR, '**/*.js')
        except curio.CancelledError:
            await wg.cancel_remaining()
            print(f"file watchers cancelled")
            raise


async def app_instance():
    print(f"starting app server")
    tests_started = False
    app = subprocess.Popen(FUNCTION_CALL.split(' '),
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE)
    try:
        while True:
            out = await app.stdout.readline()
            if out is not b'':
                print(out.decode('utf-8').strip())
                if not tests_started:
                    tests_started = True
                    print(f"starting tests")
                    await start_tests.set()
    except curio.CancelledError:
        app.terminate()
        print(f"app instance cancelled")
        raise


async def test_instance():
    await start_tests.wait()
    print(f"starting tests server")
    tests = subprocess.Popen(['pytest', '-v', '--pyargs', 'bonham'],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)
    try:
        while True:
            out = await tests.stdout.readline()
            if out is not b'':
                print(out.decode('utf-8').strip())
    except curio.CancelledError:
        tests.terminate()
        print(f"tests instance cancelled")
        raise


async def manager(cmd_args):
    print(cmd_args)
    print(f"starting task manager")
    while True:
        try:
            async with curio.TaskGroup() as tg:
                await tg.spawn(app_instance)
                if cmd_args.with_tests:
                    await tg.spawn(test_instance)
                fw = await tg.spawn(file_watchers, cmd_args.watch_js)
                await fw.join()
                await tg.cancel_remaining()
                print(f"restarting")
        except curio.CancelledError:
            await tg.cancel_remaining()
            print(f"task manager cancelled")
            return


def main():
    logging.basicConfig(level=logging.INFO)
    parser = ArgumentParser('Run a Bonham Development Server.')
    parser.add_argument('--debug', '-d', action='store_true',
                        help='turn debug on.')
    parser.add_argument('--watch-js', '-wjs', action='store_true',
                        help='watch changes in javascript files too.')
    parser.add_argument('--with-tests', '-wt', action='store_true',
                        help='run with test runner.')
    parser.add_argument('--port', '-p', type=int, default=9090,
                        help='port number for this server instance, type integer default 9090')
    args = parser.parse_args()
    try:
        curio.run(manager, args, with_monitor=True)
    except Exception as e:
        print(type(e).__name__, e)

if __name__ == '__main__':
    main()
