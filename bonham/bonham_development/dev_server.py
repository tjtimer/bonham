"""
Bonham Development Server
Author: Tim Jedro
Version: 0.0.1a1 completely (uv)loop based

"""
import asyncio
from asyncio import Task
import datetime
import logging
from pathlib import Path
import signal

import arrow
import sys
from uvloop import EventLoopPolicy

from bonham.bonham_development.settings import *
from bonham.utils import prepared_uvloop

asyncio.set_event_loop_policy(EventLoopPolicy())

logging.getLogger('asyncio').setLevel(logging.DEBUG)

async def modified_files(*, root_dir=None, pattern=None):
    return {file.name for file in root_dir.glob(pattern)
            if (arrow.now() - arrow.get(os.stat(file).st_mtime)) <= datetime.timedelta(seconds=1)
            and file.name != __file__}


async def file_watcher(*, root_dir=None, glob_patterns=None):
    try:
        if root_dir is None:
            root_dir = Path(ROOT_DIR)
        if glob_patterns is None:
            glob_patterns = GLOB_PATTERNS
        while True:
            #  sleep for 1 second
            await asyncio.sleep(1)
            #  collect modified file(s)
            for pattern in glob_patterns:
                _modified_files = await modified_files(root_dir=root_dir, pattern=pattern)
                if len(_modified_files):
                    sys.stdout.write(f"\nmodified files: {_modified_files}\n")
                    return
    except Exception as e:
        sys.stdout.write(f"\n\n{type(e).__name__} at file_watcher()")
        raise

async def process_output(proc, prefix=None):
    try:
        if prefix is None:
            prefix = f"{proc.pid} ->\n\t"
        while True:
            if proc.stdout.at_eof():
                sys.stdout.write(f"{prefix}\nreceived EOF\nend process output {proc.pid}\n\n")
                return
            data = (await proc.stdout.readline()).decode('ascii').rstrip()
            if data is not b'':
                sys.stdout.write(f"{prefix}\n\t{data}\n\n")
    except Exception as e:
        sys.stdout.write(f"\n\n{type(e).__name__} at process_output() with prefix {prefix}")
        raise


async def dev_server():
    """
    This is the actual development server.
    It spawns two processes, the file_watcher, returning the modified file(s)
    and the one that runs the program/function, you're working on.
    It returns and will be restarted if one of both processes returns or exited with an Exception.
    
    """
    function_call = FUNCTION_CALL
    proc = await asyncio.create_subprocess_shell(f"{function_call}", stdout=asyncio.subprocess.PIPE)
    child_pid = proc.pid + 1
    tests = await asyncio.create_subprocess_shell(f"pytest tests", stdout=asyncio.subprocess.PIPE)
    tests_child_pid = tests.pid + 1
    sys.stdout.write(f"bonham-dev-server is running. Type CTRL+C to cancel.\n\n")
    try:
        asyncio.ensure_future(process_output(tests, prefix=f"tests {tests.pid} {'*'*10} ->"))
        asyncio.ensure_future(process_output(proc, prefix=f"\n{proc.pid} {function_call}: "))
        await file_watcher()
        sys.stdout.write(f"subprocess tests: {tests}\n")
        sys.stdout.write(f"killing child process {child_pid}\n")
        os.kill(child_pid, signal.SIGTERM)
        if tests.returncode is None:
            sys.stdout.write(f"killing tests: {tests.pid}")
            os.kill(tests_child_pid, signal.SIGTERM)
            tests.terminate()
            os.kill(tests.pid, signal.SIGTERM)
        #  call main to restart the dev_server
        await clean_up(True)
    except asyncio.CancelledError:
        sys.stdout.write("\nCancelledError at dev_server()\n")
        sys.stdout.write(f"subprocess tests: {tests}\n")
        sys.stdout.write(f"killing child process {child_pid}\n")
        os.kill(child_pid, signal.SIGTERM)
        if tests.returncode is None:
            sys.stdout.write(f"killing tests: {tests.pid}")
            os.kill(tests_child_pid, signal.SIGTERM)
            tests.terminate()
            os.kill(tests.pid, signal.SIGTERM)
        await clean_up()
    except ProcessLookupError:
        await clean_up()


async def clean_up(restart=None):
    for task in Task.all_tasks():
        if not task == Task.current_task():
            task.cancel()
    if restart:
        return main()
    return


def main():
    """
    (re)starting the development server.
    browser should be an subprocess which is running an instance of selenium.webdriver
    """
    loop = prepared_uvloop(debug=True)
    try:
        loop.run_until_complete(dev_server())
    except KeyboardInterrupt:
        sys.stdout.write("KeybordInterrupt at main()")
        loop.run_until_complete(clean_up())
    except RuntimeError:
        loop.run_until_complete(clean_up())
        loop.stop()
        loop.close()
        main()
    except Exception as e:
        sys.stdout.write(f"Exception in main()\n\t{type(e).__name__}: {e}\n")
    finally:
        if loop.is_running():
            loop.stop()
        if not loop.is_closed():
            loop.close()
        sys.stdout.write(f"\n\n{'*'*10}Successfully shut down DEV SERVER{'*'*10}\n")

if __name__ == '__main__':
    main()
