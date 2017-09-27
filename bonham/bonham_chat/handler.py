"""
Name: bonham - handler 
Author: Tim "tjtimer" Jedro
Email: tjtimer@gmail.com
Version: 0.0.1dev

created: 21.09.17 09:51
"""

import logging

import aiohttp

from bonham.bonham_auth.decorators import authentication_required
from bonham.bonham_chat.models import Chat
from bonham.bonham_core.decorators import db_connection, load_data
from bonham.bonham_core.web_sock import ChatSocket

__all__ = ()

logger = logging.getLogger(__name__)


@authentication_required
@load_data
@db_connection
async def chat_handler(request):
    sender_id = request['access_token']['id']
    receiver_ids = request['data']['receiver_ids']  # must be list or tuple
    chat_room = Chat(id=request._match_info['room_id'])
    ws = ChatSocket(request, chat_room)
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
