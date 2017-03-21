import asyncio

from aiohttp import web
from passlib.hash import pbkdf2_sha512
from sqlalchemy.exc import IntegrityError

from .models import Account
from .token import Token


async def sign_up(request):
    await asyncio.sleep(5)
    account = Account(**request['data'])
    try:
        async with request['connection'].transaction():
            await account.create(connection=request['connection'])
            token = await Token(loop=request.app.loop).create(payload=dict(id=account.id, email=account.email))
            acc_serialized = await account.serialized()
            response = {
                'account': acc_serialized,
                'message': {
                    'type'   : 'message',
                    'message': 'we send you an email with a link to verify and finish the sign up process.'
                    }
                }
            headers = {
                'AUTH-TOKEN': token
                }
            return web.json_response(response, headers=headers)
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
    await asyncio.sleep(5)
    try:
        account = Account(email=request['data']['email'], logged_in=True)
        await account.update(connection=request['connection'], key='email')
        password_is_correct = pbkdf2_sha512.verify(request['data']['password'], account.password)
        if password_is_correct:
            token = await Token(loop=request.app.loop).create(payload=dict(id=account.id, email=account.email))
            acc_serialized = await account.serialized()
            tables = {t.name: [item.name for item in t.columns] for t in account.metadata.sorted_tables}
            response = {
                'account': acc_serialized,
                'tables' : tables,
                'message': {
                    'type': 'message',
                    'message': 'successfully logged in'
                    }
                }
            headers = {
                'AUTH-TOKEN': token
                }
            print(response, token)
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
    request['account'].logged_in = True
    await asyncio.sleep(5)
    try:
        await request['account'].update(connection=request['connection'])
        token = await Token(loop=request.app.loop).create(
                payload=dict(id=request['account'].id, email=request['account'].email)
                )
        acc_serialized = await request['account'].serialized()
        tables = {t.name: [item.name for item in t.columns] for t in request['account'].metadata.sorted_tables}
        headers = {
            'AUTH-TOKEN': token
            }
        response = {
            'account': acc_serialized,
            'tables' : tables,
            'message': {
                'type'   : 'message',
                'message': f"welcome back {request['account'].email}!"
                }
            }
        return web.json_response(response, headers=headers)
    except Exception as e:
        print(type(e).__name__, e)
        raise


async def logout(request):
    await asyncio.sleep(5)
    try:
        request['account'].logged_in = False
        await request['account'].update(connection=request['connection'])
        response = {
            'message': {
                'type'   : 'message',
                'message': f"{request['account'].email} successfully logged out."
                }
            }
        return web.json_response(response)
    except Exception as e:
        print(type(e).__name__, e)
        raise
