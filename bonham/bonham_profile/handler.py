import base64
from io import BytesIO
import os

from aiohttp import web

from bonham.bonham_media.functions import process_image
from bonham.bonham_profile.constants import Connection
from bonham.bonham_profile.models import Friend, Profile
from bonham.settings import UPLOAD_DIR


async def get_user(request):
    user = Profile()
    try:
        user_data = await user.get_by_id(request['connection'], id=request['data']['id'])
        vars(user).update(**user_data)
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
    user = Profile()
    print('get_users request:\n\t{}'.format(request['query_string']))
    try:
        if 'account' not in request.keys():
            users = list(await Profile(**data).serialized() for data in
                         await user.get(request['connection'], **request['query_string']))
        else:
            users = list(await Profile(**data).serialized() for data in
                         await user.get(request['connection'], **request['query_string'])
                         if data['id'] != request['account']['id'])
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
        vars(request['user']).update(**request['data'])
        await request['user'].update(request['connection'])
        user_serialized = await request['user'].serialized()
        response = {
            'message': 'update success',
            'user':    user_serialized
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
        return web.json_response({'message': 'object deleted'})
    except Exception as e:
        print('delete user exception:\n\t{}\n\t{}'.format(type(e).__name__, e))
        raise


# friends

async def get_friends(request):
    try:
        user = Profile(id=request.match_info['id'])
        friends = await user.get_friends(request['connection'])
        return web.json_response(friends, status=200)
    except Exception as e:
        print('get friends exception:\n\t{}\n\t{}'.format(type(e).__name__), e)


async def request_friendship(request):
    try:
        await Friend(
                user_id=request['user'].id,
                friend_id=request['data']['user_id'],
                friendship=Connection.requested).create(request['connection'])
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
