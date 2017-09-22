"""
Name: bonham - manager 
Author: Tim "tjtimer" Jedro
Email: tjtimer@gmail.com
Version: 0.0.1dev

created: 04.09.17 18:12
"""
import asyncio
import logging
import logging.config
import os
import signal
from pathlib import Path

import arrow
import uvloop

from bonham.bonham_core.helper import BLoop, load_yaml_conf
from bonham.settings import CONF_DIR

__all__ = ()

logger_config = load_yaml_conf(Path(CONF_DIR).joinpath('logging.conf.yaml'))
logging.config.dictConfig(logger_config)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class ManagerProtocol(asyncio.subprocess.SubprocessStreamProtocol):

    def __init__(self, message_queue, limit, loop):
        super().__init__(limit=limit, loop=loop)
        self.messages = message_queue
        self._pipe_fds = [self.stdin, self.stdout, self.stderr]

    @property
    def no_streams(self):
        return all(pipe is None for pipe in self._pipe_fds)

    def send(self, msg):
        self.messages.put_nowait(msg)

    def connection_made(self, transport):
        self._transport = transport
        stdin_transport = transport.get_pipe_transport(0)
        if stdin_transport is not None:
            self.stdin = asyncio.streams.StreamWriter(stdin_transport,
                                                      protocol=self,
                                                      reader=None,
                                                      loop=self._loop)
            self._pipe_fds[0] = self.stdin

        stdout_transport = transport.get_pipe_transport(1)
        if stdout_transport is not None:
            self.stdout = asyncio.streams.StreamReader(limit=self._limit,
                                                       loop=self._loop)
            self.stdout.set_transport(stdout_transport)
            self._pipe_fds[1] = self.stdout

        stderr_transport = transport.get_pipe_transport(2)
        if stderr_transport is not None:
            self.stderr = asyncio.streams.StreamReader(limit=self._limit,
                                                       loop=self._loop)
            self.stderr.set_transport(stderr_transport)
            self._pipe_fds[2] = self.stderr

    def pipe_data_received(self, fd, data):
        if fd in [1, 2]:
            reader = self._pipe_fds[fd]
            if reader is not None:
                if len(reader._buffer):  # delete unread data from reader
                    reader._buffer = bytearray()
                reader.feed_data(data)
        self.send(f"{self._pipe_fds[fd]}:\n{data.decode()}")

    def pipe_connection_lost(self, fd, exc):
        pipe = self._pipe_fds[fd]
        if pipe is not None:
            if fd == 0:
                pipe.close()
                return
            else:
                if exc is None:
                    pipe.feed_eof()
                else:
                    pipe.set_exception(exc)
            self._pipe_fds[fd] = None
        self.send(f"{self._pipe_fds[fd]} connection_lost: {exc}")
        self._maybe_close_transport()

    def process_exited(self):
        self._process_exited = True
        self._maybe_close_transport()

    def _maybe_close_transport(self):
        if self.no_streams and self._process_exited:
            self.send("closing transport")
            self._transport.close()
            self._transport = self._pipe_fds = None


class Manager(object):
    r"""Manager
    handles multiple processes.
    """

    def __init__(self, debug=False):
        if debug:
            logger.setLevel(logging.DEBUG)
        self._loop = BLoop(debug=debug)
        self._is_running = asyncio.Event()
        self._stopped = asyncio.Event()
        self._processes = {}
        self._processes_running = []
        self._processes_stopped = []
        self._processes_to_start = []
        self._processes_to_stop = []
        self.pid = os.getpid()
        self.messages = asyncio.Queue()
        signal.signal(signal.SIGINT, self.shutdown)

    @property
    def is_running(self):
        return self._is_running.is_set()

    @property
    def stopped(self):
        return self._stopped.is_set()

    @property
    def tasks(self):
        return asyncio.Task.all_tasks()

    def spawn(self, name, command):
        r"""spawn a process"""
        message_queue = asyncio.Queue()
        self.messages.put_nowait(f"{f'spawning {name} process':*^80}")
        coro = self._loop.subprocess_exec(
            lambda: ManagerProtocol(
                message_queue=message_queue,
                limit=2 ** 16,
                loop=self._loop
                ),
            *command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)
        transport, protocol = self._loop.run_until_complete(coro)
        process = asyncio.subprocess.Process(
            transport=transport, protocol=protocol, loop=self._loop
            )
        assert name not in self._processes.keys(), \
            f"process name {name} already in use. {self._processes[name]}"
        reporter = self._loop.create_task(self.report(message_queue))
        self._processes[name] = dict(
            process=process, reporter=reporter,
            started=arrow.now()
            )
        self._processes_running.append(name)
        return process

    def start_all(self):
        r"""start all processes"""

    def stop(self, name):
        r"""stop one process"""
        print(f"{f'stopping {name} process':*^80}")
        self._processes[name]['process'].terminate()
        if name in self._processes_running:
            self._processes_running.remove(name)
        self._processes_stopped.append(name)

    def stop_all(self):
        r"""stop all processes"""
        for name in self._processes_running:
            self.stop(name)

    async def send(self, name, msg):
        r"""send message to given process"""
        await self._processes[name].communicate(input=msg)

    async def broadcast(self):
        r"""send msg to all running processes"""

    async def report(self, message_queue):
        messages = message_queue
        await self._is_running.wait()
        while self.is_running:
            msg = await messages.get()
            print(f"{msg}\n")
        print(f"reporting stopped")

    def setup(self):
        r"""setup manager"""
        self._loop.create_task(self.report())

    def shutdown(self, *args):
        if self.stopped:
            return
        self._is_running.clear()
        self.stop_all()
        self.messages = None
        for task in self.tasks:
            task.cancel()
            if task._state == 'PENDING':
                task.set_exception(asyncio.CancelledError)
        self._stopped.set()
        logger.debug(f"bye")
        return self._loop.close()

    def run(self):
        self._is_running.set()
        logger.debug(
            f"Manager running with pid {self.pid}"
            f"\n\tself: {vars(self)}"
            )
        try:
            self._loop.run_forever()
        except:
            logger.debug("exception at run")
            self.shutdown()

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb, *args):
        print(f"Manager.stopped: {self.stopped}")
        self.shutdown()


def main():
    with Manager(debug=True) as mngr:
        mngr.spawn(
            'service_1',
            command=(
                'python', '/var/www/projects/bonham/bonham/root.py'
                )
            )
        mngr.run()


if __name__ == '__main__':
    main()
