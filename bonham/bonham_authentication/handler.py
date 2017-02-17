from aiohttp import web
from sqlalchemy.exc import IntegrityError

from bonham.bonham_user.models import User
from .token import Token


async def sign_up(request):
    token = Token()
    user = User(**request['data'])
    try:
        await user.create(request['connection'])
        token = await token.create(user.__dict__)
        user_serialized = await user.serialized()
        response = {
            'user': user_serialized,
            'message': {
                'type': 'message',
                'message': 'we send you an email with a link to verify and finish the sign up process.'
            }
        }
        headers = {
            'AUTH-TOKEN': token
        }

        _response = web.json_response(response, headers=headers)
        return _response
    except IntegrityError as e:
        response = {
            'message': {
                'type': 'error',
                'message': '{}'.format(e)
            }
        }
        return web.json_response(response, status=401)
    except Exception as e:
        print(type(e).__name__, e)
        raise


async def login(request):
    token = Token()
    try:
        user = User(email=request['data']['email'], logged_in=True)
        await user.update(request['connection'], key='email')
        password_is_correct = request['data']['password'] == user.password
        if password_is_correct:
            token = await token.create(user.__dict__)
            user_serialized = await user.serialized()
            tables = { t.name: [item.name for item in t.columns] for t in
                       user.metadata.sorted_tables }
            response = {
                'user': user_serialized,
                'tables': tables,
                'message': {
                    'type': 'message',
                    'message': 'successfully logged in'
                }
            }
            headers = {
                'AUTH-TOKEN': token
            }
            return web.json_response(response, headers=headers)
        else:
            response = {
                'message': {
                    'type': 'error',
                    'message': 'wrong password'
                }
            }
            return web.json_response(response, status=401)
    except Exception as e:
        print(type(e).__name__, e)
        raise


async def token_login(request):
    token = Token()
    request['user'].logged_in = True
    try:
        await request['user'].save(request['connection'])
        friends = list((await request['user'].get_friends(request['connection'])))
        token = await token.create(request['user'].__dict__)
        user_serialized = await request['user'].serialized()
        tables = { t.name: [item.name for item in t.columns] for t in
                   request['user'].metadata.sorted_tables }
        headers = {
            'AUTH-TOKEN': token
        }
        response = {
            'user': user_serialized,
            'tables': tables,
            'friends': friends,
            'message': {
                'type': 'message',
                'message': 'welcome back dumdidum {}!'.format(request['user'].name)
            }
        }
        return web.json_response(response, headers=headers)
    except Exception as e:
        print(type(e).__name__, e)
        raise


async def logout(request):
    try:
        request['user'].__dict__['logged_in'] = False
        await request['user'].update(request['connection'])
        response = {
            'message': {
                'type': 'message',
                'message': '{} successfully logged out'.format(request['user'].name)
            }
        }
        return web.json_response(response)
    except Exception as e:
        print(type(e).__name__, e)
        raise
