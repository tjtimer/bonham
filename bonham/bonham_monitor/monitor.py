from asyncio import Event, gather

from curio import tcp_server

from bonham import Service
from bonham.settings import MONITOR_HOST, MONITOR_PORT


class Monitor(Service):
    def __init__(self):
        super().__init__()
        self._connection_made = Event()
        self._run_monitor = self.monitor_stream_server(MONITOR_HOST,
                                                       MONITOR_PORT)

    async def dispatcher(self):
        async for msg in messages:
            for q in audience:
                print(f"subscriber: {q}\nmessage: {msg}")
                await q.put(msg)

    async def publish(self, msg):
        await self.messages.put(msg)

    async def broadcast(self, client_stream):
        print(f"\n\tclient_stream outgoing: {client_stream}")
        source = Queue()
        try:
            audience.add(source)
            print(f"\tsource: {source}\n\taudience: {audience}")
            async for msg in source:
                await client_stream.write(msg)
        finally:
            audience.discard(source)

    async def monitor(self, msg, **kwargs):
        if msg not in ['', b'', False, None]:
            if connection_made.is_set():
                await self.publish(('TODO: channel name/topic', msg))
            else:
                stack = inspect.stack()
                sender = kwargs.pop('sender', (stack[1][3], stack[1][2]))
                print(f"directly put ({(sender, msg)}) to queue")
                return await messages.put((sender, msg))

    async def monitoring_handler(self, client, addr):
        try:
            log.info('Connection from %r', addr)
            async with client:
                await self._connection_made.set()
                await self.report(f"\n\nclient:\t{client}")
                client_stream = client.as_stream()
                await client_stream.write(b'Your name: ')
                name = (await client_stream.readline()).strip()
                await self.report(f"{name} logged into monitorview")
                await gather(
                    self.broadcast(self.stream),
                    self.read(self.stream, name)
                    )
            await self.report(f"{name} left\n\n\tclient: {client}")
        except Exception as e:
            connection_made.clear()
            await self.report(
                f"Exception {type(e).__name__}: {e}\nat\nclient: {client}")

        log.info('%r connection closed')

    async def monitor_stream_server(self, host, port):
        async with TaskGroup() as g:
            await g.spawn(self.dispatcher)
            await g.spawn(tcp_server, host, port, self.monitoring_handler,
                          {'ssl': get_ssl_context()})

    async def run(self):
        while True:
            #  print(f"starting monitor service at http://{MONITOR_HOST}:{
            # MONITOR_PORT}/")
            self.task = await spawn(self._run_monitor)
            await self._ready.set()
            await self.report(f"monitor task: {task}\nready: {self._ready}")
            res = await self.task.join()
            print(f"monitor task: {self.task}\nres: {res}")
