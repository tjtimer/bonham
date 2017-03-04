"""
Bonham Development Server
Author: Tim Jedro
Version: 0.0.1a1 protocol based

"""
import arrow
import asyncio
import datetime
import os
import signal
import uvloop
from asyncio import Task
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from bonham.settings import BASE_DIR

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class MySubProtocol(asyncio.SubprocessProtocol):
    def __init__(self, exit):
        super().__init__()
        self.output = bytearray()
        self.exit = exit
        self.transport = None
        self.child_pid = None
        print(f"subprocess_shell started.\nprotocol: {self.__dict__}\n")

    def connection_made(self, transport):
        self.transport = transport
        self.child_pid = self.transport.get_pid() + 1
        print(f"subprocess_shell connected.\nprotocol: {self.__dict__}\n")

    def pipe_data_received(self, fd, data):
        self.output.extend(data)

    def pipe_connection_lost(self, fd, exc):
        print(self.__dict__)

    def process_exited(self):
        self.exit.set_result(True)

    def read(self):
        current_output = bytes(self.output)
        self.output = bytearray()
        return current_output if current_output != bytearray() else None

    def stop(self):
        print(f"killing server")
        if self.child_pid:
            print(f"killing child process with pid {self.child_pid}")
            os.kill(self.child_pid, signal.SIGTERM)
        self.transport.terminate()
        self.transport.close()
        self.exit.set_result(True)


async def file_watcher(*, loop=None):
    while True:
        await asyncio.sleep(0.5)
        changed_files = { pyfile.name for pyfile in Path(BASE_DIR).glob('**/*.py')
                          if (arrow.now() - arrow.get(os.stat(pyfile).st_mtime))
                          <= datetime.timedelta(seconds=1) }
        if len(changed_files):
            return changed_files


async def server(*, loop=None):
    exit_a = asyncio.Future(loop=loop)
    fw = asyncio.ensure_future(file_watcher(loop=loop), loop=loop)
    sub_a_transport, sub_a_protocol = await loop.subprocess_shell(
            lambda: MySubProtocol(exit_a),
            f"clear && python root.py",
    )
    await asyncio.sleep(0.5)
    print('#' * 40)
    print(f"sub_a_transport: {sub_a_transport}")
    print(f"sub_a_protocol: {sub_a_protocol}")
    print('#' * 40)
    while not fw.done():
        data = sub_a_protocol.read()
        if data:
            print(data.decode('ascii').rstrip())
        await asyncio.sleep(1)
    sub_a_protocol.stop()
    await exit_a
    print()
    print('*' * 10, f'restart after file {fw.result()} changed', '*' * 10)
    return main()


def prepared_uvloop(*, loop=None, debug=None):
    if loop is None or loop.is_closed():
        loop = uvloop.new_event_loop()
        asyncio.set_event_loop(loop)
    if debug:
        loop.set_debug(True)
    loop.set_default_executor(ProcessPoolExecutor())
    return loop


def main():
    loop = prepared_uvloop(debug=True)
    try:
        loop.run_until_complete(server(loop=loop))
    except KeyboardInterrupt:
        print(f"KeyboardInterrupt at main()")
        for task in Task.all_tasks():
            task.cancel()
        pass
    finally:
        print(f"main finally")
        loop.close()


if __name__ == '__main__':
    main()
