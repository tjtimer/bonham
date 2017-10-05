"""
Bonham Development Server
Author: Tim Jedro
Version: 0.0.1a1 curio based

"""
import argparse
import asyncio
import logging
import os
import pathlib
import signal
import sys
import time
from difflib import HtmlDiff

import aiofiles
import arrow

from bonham.bonham_core.helper import BLoop
from bonham.settings import LOG_DIR

log = logging.getLogger(__file__)
log_file = logging.FileHandler(os.path.join(LOG_DIR, f"{__name__}.log"))
log.addHandler(log_file)

# constants
SERVICE_CMD = ['python', '-c', 'print(1 + 1)']
TESTS_CMD = ['pytest', '-v', '--pyargs', 'bonham']
ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
GLOB_PATTERN = '**/*.py'

parser = argparse.ArgumentParser('Run a Bonham Development Server.')
parser.add_argument('--debug', '-d', action='store_true',
                    help='turn debug on.')
parser.add_argument('--watch-js', '-wjs', action='store_true',
                    help='watch changes in javascript files too.')
parser.add_argument('--with-tests', '-wt', action='store_true',
                    help='run with test runner.')

files = pathlib.Path(ROOT_DIR).glob(GLOB_PATTERN)


class DevServer:
    r"""DevServer
    runs application in a subprocess and
    watches all python files for changes
    """

    def __init__(self, *, loop=BLoop(), **kwargs):
        self.__dict__.update(**kwargs)
        self.app = self.tests = None
        self.restart_count = 0
        self.files_2_watch = {}
        self._loop = loop
        self.code_differ = HtmlDiff()
        self._is_running = asyncio.Event()
        self._file_changed = asyncio.Event()

        self._loop.run_until_complete(
            asyncio.gather(*(
                self.load_file(file)
                for file in files
                ))
            )

    @property
    def is_running(self):
        return self._is_running.is_set()

    @property
    def file_changed(self):
        return self._file_changed.is_set()

    async def get_code(self, path):
        async with aiofiles.open(path, 'r') as file:
            code = await file.read()
        return code

    async def load_file(self, file):
        if os.path.isfile(file):
            self.files_2_watch[file] = dict(
                last_modified=os.stat(file).st_mtime)

    async def write_diff(self, diff: str):
        async with aiofiles.open('diff.html', 'wb') as file:
            file.write(diff)

    async def check_mtime(self, file):
        changed = self.files_2_watch[file]['last_modified'] != os.stat(
            file).st_mtime
        if changed:
            self.files_2_watch[file]['last_modified'] = os.stat(file).st_mtime
            await self.report(f"file {file} changed!\n")
            self._file_changed.set()

    async def watch_files(self):
        i = 0  # set/reset 'timer'
        await self.report(
            f"files_2_watch size: "
            f"{int(self.files_2_watch.__sizeof__() / 1024.0)} mb\n"
            )
        await self._is_running.wait()  # wait for
        await self.report('start to watch files')
        while self.is_running and not self.file_changed:
            await asyncio.sleep(1)
            await asyncio.gather(*(
                self._loop.create_task(self.check_mtime(file))
                for file in self.files_2_watch.keys()
                ))
            i += 1
            # stop dev-server if no file changed
            # within 10 minutes
            if i >= 10:
                self._is_running.clear()

    async def run_service(self):
        log.info(f"starting app process")
        self.app = await asyncio.create_subprocess_exec(
            'python', '/var/www/projects/bonham/bonham/root.py',
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            loop=self._loop
            )
        await self.report(f"app process: {self.app}")
        self._is_running.set()
        async for line in self.app.stdout:
            await self.report(line.decode('utf-8'))

    async def run_tests(self):
        await self._is_running.wait()
        log.info(f"starting test_runner")
        self.tests = await asyncio.create_subprocess_exec(
            *TESTS_CMD,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            loop=self._loop
            )
        await self.report('tests started')
        try:
            async for line in self.tests.stdout:
                if not self.is_running:
                    return
                await self.report(line.strip())
        except (OSError, asyncio.CancelledError):
            self.tests.terminate()

    async def manager(self):
        r"""start application and watch project files for changes
            return when application finished with an exception or
            file watcher detects changed file.
        """
        try:
            await self.report(f"manager: starting {self.restart_count}")
            tasks = await asyncio.wait([
                asyncio.ensure_future(self.watch_files()),
                asyncio.ensure_future(self.run_service()),
                asyncio.ensure_future(self.run_tests())
                ],
                return_when=asyncio.FIRST_COMPLETED
                )
            await self.report(f"tasks returned: {tasks}")
            await self.report(f"app task: {self.app}")
            if self.app is not None:
                self.app.send_signal(signal.SIGTERM)  # send CTRL + C
                await self.app.wait()  # wait until app did shutdown
                await self.app._loop.shutdown_asyncgens()
                if not self.app._transport.is_closing():
                    self.app.terminate()
                self.app._loop.stop()
                # ret = await self.app.wait()
                # await self.report(f"self.app.wait() returned: {ret}")
                # print(self.app, self.app._transport)
        except asyncio.CancelledError as e:
            print(f"received CanceledError: {e}")
            raise

    async def report(self, msg: str):
        return sys.stdout.write(f"\n{msg}")

    def stop(self):
        self._is_running.clear()
        for task in asyncio.Task.all_tasks():
            if not task.cancelled():
                print(f"\ncancelling {task}")
                task.cancel()
                if task._state != 'FINISHED':
                    task.set_exception(asyncio.CancelledError())
                    print(f"task exception set.\n")
                    print(f"task._state: {task._state}\n")


def run():
    loop = BLoop(debug=True)
    dev_server = DevServer(loop=loop)
    try:
        loop.run_until_complete(dev_server.manager())
        if dev_server.is_running:
            if dev_server.file_changed:
                dev_server._file_changed.clear()
            print(f"\n\n\nRESTARTING DevServer at {arrow.now()}\n\n\n")
            return run()
    except KeyboardInterrupt:
        print(f"\n{arrow.now()}: KeyboardInterrupt at dev_server.py run()")
        dev_server.stop()

        time.sleep(3)
        print(f"loop: {vars(dev_server.app)}")
    except Exception as e:
        print(f"Exception: {type(e).__name__}, {e}")
        dev_server.stop()
        time.sleep(5)
        run()
    finally:
        loop.stop()
        loop.close()


if __name__ == '__main__':
    run()
