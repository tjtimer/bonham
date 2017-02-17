import base64
import os
from aiohttp import web
from io import BytesIO
from sqlalchemy import and_

from bonham.bonham_media.functions import process_image
from bonham.bonham_user.constants import Friendship
from bonham.bonham_user.models import Friend, User
from bonham.settings import UPLOAD_DIR


async def get_user(request):
    user = User()
    try:
        user_data = await user.get(request['connection'], where=and_(user.__table__.c.id == request['data']['id']))
        user.__dict__.update(**(list(user_data)[0]))
        response = await user.serialized()
        return web.json_response(response, status=200)
    except IndexError:
        response = {
            'message': {
                'type': 'error',
                'message': 'user not found'
            }
        }
        return web.json_response(response, status=400)


async def get_users(request):
    qs = request.rel_url.query_string
    if qs:
        kwargs = { pair.split('=')[0]: pair.split('=')[1] for pair in qs.split('&') }
    else:
        kwargs = {
            'offset': 0,
            'order_by': 'name',
            'limit': 50
        }
    print('get_users request:\n\t{}'.format(kwargs))
    try:
        users = []
        for data in await request['user'].get(request['connection'], **kwargs):
            if data['id'] != request['user'].id:
                users.append((await User(**data).serialized()))
        return web.json_response(users)
    except Exception as e:
        print(e)
        raise


async def update_user(request):
    try:
        if 'avatar' in request['data'].keys():
            file_data = request['data']['avatar']['data'].split(',')
            if file_data is not None:
                request['data']['avatar'] = await process_image(
                        BytesIO(base64.b64decode(file_data[1])),
                        request['data']['avatar']['filename'],
                        os.path.join(UPLOAD_DIR, request['user'].name, 'images', 'avatars'))
        request['user'].__dict__.update(**request['data'])
        await request['user'].update(request['connection'])
        user_serialized = await request['user'].serialized()
        response = {
            'message': {
                'type': 'message',
                'message': 'update success'
            },
            'user': user_serialized
        }
        return web.json_response(response, status=200)
    except Exception as e:
        print(e)
        response = {
            'message': {
                'type': 'error',
                'message': 'You\'re not allowed to change this data.'
            }
        }
        return web.json_response(response, status=401)


async def delete_user(request):
    try:
        await request['user'].delete(request['connection'])
        return web.json_response(
                {
                    'message': {
                        'type': 'message',
                        'message': 'object deleted'
                    }
                }
        )
    except Exception as e:
        print('delete user exception:\n\t{}\n\t{}'.format(type(e).__name__, e))
        raise


# friends

async def get_friends(request):
    try:
        user = User(id=request.match_info['id'])
        friends = await user.get_friends(request['connection'])
        return web.json_response(friends, status=200)
    except Exception as e:
        print('get friends exception:\n\t{}\n\t{}'.format(type(e).__name__), e)


async def request_friendship(request):
    try:
        await Friend(
                user_id=request['user'].id,
                friend_id=request['data']['user_id'],
                friendship=Friendship.requested).create(request['connection'])
        response = {
            'message': {
                'type': 'message',
                'message': 'friend request success'
            }
        }
        return web.json_response(response)
    except Exception as e:
        print('request friendship exception:\n\t{}\n\t{}'.format(type(e).__name__, e))
        raise


async def update_friendship(request):
    pass
