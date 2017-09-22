"""
Name: bonham - handler 
Author: Tim "tjtimer" Jedro
Email: tjtimer@gmail.com
Version: 0.0.1dev

created: 21.09.17 09:51
"""

import logging

import aiohttp
from aiohttp import web

__all__ = ()

logger = logging.getLogger(__name__)


@token_data
async def chat_handler(request):
    ws = web.WebSocketResponse()
    sender_id = request['token_data']['id']
    receiver_ids = request['data']['receiver_ids']  # must be list or tuple
    await ws.prepare(request)
    if sender_id not in request.app['websockets'].keys():
        request.app['websockets'][sender_id] = {}
    request.app['websockets'][sender_id]['-'.join(receiver_ids)] = ws

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:
                await ws.send_str(msg.data + '/answer')
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())

        print('websocket connection closed')

        return ws
