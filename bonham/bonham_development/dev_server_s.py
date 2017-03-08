"""
Bonham Development Server
Author: Tim Jedro
Version: 0.0.1a1 completely (uv)loop based

"""
import asyncio
import datetime
import signal
import time
from asyncio import Task

import arrow
import logging
import os
from pathlib import Path

from bonham.bonham_development.settings import *
from bonham.settings import ROOT_FILE
from bonham.utils import prepared_uvloop

logging.getLogger('asyncio').setLevel(logging.DEBUG)


def sleep():
    time.sleep(10)
    print("10 seconds gone since start up")


async def modified_files(*, root_dir=None, pattern=None):
    _mf = { file.name for file in root_dir.glob(pattern)
            if (arrow.now() - arrow.get(os.stat(file).st_mtime)) <= datetime.timedelta(seconds=1) }
    return _mf


async def file_watcher(*, root_dir=None, glob_patterns=None):
    if root_dir is None:
        root_dir = Path(ROOT_DIR)
    if glob_patterns is None:
        glob_patterns = GLOB_PATTERNS
    while True:
        #  sleep for 0.5 seconds
        await asyncio.sleep(1)
        #  collect modified file(s)
        for pattern in glob_patterns:
            _modified_files = await modified_files(root_dir=root_dir, pattern=pattern)
            if len(_modified_files):
                print(f"modified files: {_modified_files}")
                return


async def process_output(proc, prefix=None):
    if prefix is None:
        prefix = "->"
    while not proc.stdout.at_eof():
        data = await proc.stdout.readline()
        if data is not b'':
            print(f"{prefix}\n{data.decode('ascii').rstrip()}\n\n")


async def dev_server(*, loop=None):
    """
    This is the actual development server.
    It spawns two processes, the file_watcher, returning the modified file(s)
    and the one that runs the program/function, you're working on.
    It returns and will be restarted if one of both processes returns or exited with an Exception.
    
    """
    #  TODO: open or reload browser, maybe record actions
    function_call = FUNCTION_CALL
    if loop is None:
        raise TypeError(f"dev_server() requires 2 keyword arguments: browser, loop")
    try:
        proc = await asyncio.create_subprocess_shell(f"{function_call}", stdout=asyncio.subprocess.PIPE)
        child_pid = proc.pid + 1
        tests = await asyncio.create_subprocess_shell(f"pytest tests", stdout=asyncio.subprocess.PIPE)
        tests_child_pid = tests.pid + 1
        print(f"bonham-dev-server is running. Type CTRL+C to cancel.")
        asyncio.ensure_future(process_output(tests, prefix=f"{tests.pid} {'*'*10} ->"))
        asyncio.ensure_future(process_output(proc, prefix=f"{proc.pid} {ROOT_FILE}: "))
        await asyncio.wait_for(file_watcher())

        print(f"subprocess tests: {tests}")
        print(f"killing child process {child_pid}")
        os.kill(child_pid, signal.SIGTERM)
        print(f"tests returncode: {tests.returncode}\ntests pid: {tests.pid}")
        if tests.returncode is None:
            print(f"killing tests: {tests.pid}")
            os.kill(tests_child_pid, signal.SIGTERM)
            tests.terminate()
            os.kill(tests.pid, signal.SIGTERM)
        clean_up()
        #  call main to restart the dev_server
        return main()
    except Exception as e:
        print(f"Exception {type(e).__name__} at dev_server: {e}.")
        raise


def clean_up():
    for task in Task.all_tasks():
        print(f"\n\ntask: {task} gets cancelled.")
        task.cancel()


def main():
    """
    (re)starting the development server.
    browser should be an subprocess which is running an instance of selenium.webdriver
    """
    loop = prepared_uvloop(debug=True)
    try:
        loop.run_until_complete(dev_server(loop=loop))
    except KeyboardInterrupt:
        clean_up()
    except Exception as e:
        print(f"Exception in main()\n\t{type(e).__name__}: {e}\n")
        clean_up()


if __name__ == '__main__':
    main()
