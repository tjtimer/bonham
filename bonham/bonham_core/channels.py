import asyncio
import logging

log = logging.getLogger(__name__)

__all__ = [
    'Channel',
    ]


class Channel:

    def __init__(self):
        self._audience = set()
        self._is_up = asyncio.Event()
        self._dispatcher = MessageDispatcher(self)
        print(vars(self), self)

    def __repr__(self):
        return f"<Channel is_up={self.is_up} subscribers={len(self.audience)}>"

    @property
    def audience(self):
        """returns set of listeners/subscribers"""
        return self._audience

    @property
    def is_up(self):
        return self._is_up.is_set()

    async def subscribe(self, listener: (asyncio.Queue,
                                         asyncio.StreamWriter,
                                         asyncio.Transport)):

        if not isinstance(listener, (asyncio.Queue, asyncio.StreamWriter,
                                     asyncio.Transport)):
            raise TypeError(f"Listener must be of type asyncio.Queue, "
                            f"asyncio.StreamWriter, asyncio.Transport")
        await self._audience.add(listener)

    async def unsubscribe(self, listener: (asyncio.Queue,
                                           asyncio.StreamWriter,
                                           asyncio.Transport)):
        await self._audience.remove(listener)

    async def open(self):
        self._is_up.set()

    async def broadcast(self, msg: bytes):
        print(f"should broadcast message: {msg}, {self._dispatcher}")
        if self.is_up:
            for listener in self._audience:
                log.debug(f"listener: {listener}\nmessage: {msg}")
                if isinstance(listener, asyncio.Queue):
                    await listener.put(msg)
                elif isinstance(listener, asyncio.StreamWriter):
                    await listener.write(msg)
                else:
                    await listener.send(msg)

    async def close(self):
        self._is_up.clear()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        print(f"channel closed: {[self, exc_type, exc_val, exc_tb]}")


class MessageDispatcher:

    def __init__(self, channel):
        self._audience = set()
        self._is_running = asyncio.Event()
        self._channel = channel
        self.messages = asyncio.Queue()

    @property
    def is_running(self):
        return self._is_running.is_set()

    async def add(self, listener):
        self._audience.add(listener)

    async def remove(self, listener):
        self._audience.remove(listener)

    async def run(self):
        self._is_running.set()
        while self._channel.is_up:
            print(f"message dispatcher waiting, {self._channel}")
            msg = await self.messages.get()
            print(f"message_dispatcher got: {msg}")
            for listener in self._audience:
                log.debug(f"listener: {listener}\nmessage: {msg}")
                if isinstance(listener, asyncio.Queue):
                    await listener.put(msg)
                elif isinstance(listener, asyncio.StreamWriter):
                    await listener.write(msg)
                else:
                    await listener.send(msg)
        self._is_running.clear()
        await self.close()

    async def __aenter__(self):
        asyncio.ensure_future(self.run())
        print(f"dispatcher __aenter__ {dispatcher}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        if self._channel.messages.empty() is False:
            await self._channel.messages.join()
