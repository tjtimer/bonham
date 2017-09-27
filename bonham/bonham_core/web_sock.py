"""
Name: bonham - web_sock 
Author: Tim "tjtimer" Jedro
Email: tjtimer@gmail.com
Version: 0.0.1dev

created: 25.09.17 19:32
"""

import asyncio
import logging

import aiohttp
from aiohttp import web

__all__ = ()

logger = logging.getLogger(__name__)


class ChatSocket(web.WebSocketResponse):

    def __init__(self, request, sender_id, receiver_ids):
        super().__init__()
        self._id = id(self)
        self._app = request.app
        self._request = request
        self._sender_id = sender_id
        self._receiver_ids = receiver_ids
        self.messages = asyncio.Queue()
        request.app.websockets['chat'][self._id] = self

    async def __aiter__(self):
        msg = await self.receive()
        if msg.type in (aiohttp.WSMsgType.CLOSE,
                        aiohttp.WSMsgType.CLOSING,
                        aiohttp.WSMsgType.CLOSED):
            raise StopAsyncIteration  # NOQA
        await self.messages.put(msg)
        return msg

    async def __aenter__(self):
        await self.prepare(self._request)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        del self._app.websockets['chat'][self._id]
