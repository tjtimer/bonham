import signal

from curio import CancelledError, Queue, SignalQueue, TaskGroup, spawn, tcp_server
from curio.socket import *

messages = Queue()
subscribers = set()


async def dispatcher():
    async for msg in messages:
        for q in subscribers:
            await q.put(msg)


async def publish(msg):
    await messages.put(msg)


# Task that writes chat messages to clients
async def outgoing(client_stream):
    queue = Queue()
    try:
        subscribers.add(queue)
        async for name, msg in queue:
            await client_stream.write(name + b':' + msg)
    finally:
        subscribers.discard(queue)


# Task that reads chat messages and publishes them
async def incoming(client_stream, name):
    try:
        async for line in client_stream:
            await publish((name, line))
    except CancelledError:
        await client_stream.write(b'SERVER IS GOING AWAY!\n')
        raise


# Supervisor task for each connection
async def chat_handler(client, addr):
    print('Connection from', addr)
    async with client:
        client_stream = client.as_stream()
        await client_stream.write(b'Your name: ')
        name = (await client_stream.readline()).strip()
        await publish((name, b'joined\n'))

        async with TaskGroup(wait=any) as workers:
            await workers.spawn(outgoing, client_stream)
            await workers.spawn(incoming, client_stream, name)

        await publish((name, b'has gone away\n'))

    print('Connection closed')


async def chat_server(host, port):
    async with TaskGroup() as g:
        await g.spawn(dispatcher)
        await g.spawn(tcp_server, host, port, chat_handler)


async def setup(app):
    async with SignalQueue(signal.SIGHUP) as restart:
        while True:
            print('Starting the server')
            serv_task = await spawn(chat_server, host, port)
            await restart.get()
            print('Server shutting down')
            await serv_task.cancel()
