from aiohttp import web
from asyncpg import UniqueViolationError
from passlib.hash import pbkdf2_sha512

from bonham.serializer import serialize
from .models import Account, validate_data
from .token import *


async def sign_up(request):
    try:
        if await validate_data(request['data']):
            async with request['connection'].transaction():
                account = await Account().create(request['connection'], data=request['data'])
                del account['password']
                payload = dict(email=account['email'], id=account['id'])
                token = await create(payload=payload)
                acc_serialized = await serialize('accounts', account)
                response = {
                    'account': acc_serialized,
                    'message': 'we send you an email with a link to verify and finish the sign up process.'
                    }
                headers = {
                    'AUTH-TOKEN': token
                    }
                return web.json_response(response, headers=headers)
        else:
            return web.json_response({'error': 'Invalid email and/or password!'}, status=400)
    except (ValueError, UniqueViolationError):
        return web.json_response({
            'error': f"account with email {request['data']['email']} already exists."
            }, status=400)


async def check_retries(failed_logins, email):
    now = datetime.datetime.now()
    since_last = now - failed_logins[email][-1]
    if len(failed_logins[email]) >= 3 and since_last <= datetime.timedelta(minutes=5):
        time_to_wait = datetime.timedelta(minutes=5) - since_last
        minutes = int(time_to_wait / 60)
        seconds = int(time_to_wait % 60)
        error_message = f"To many failed retries. Please wait for {minutes} minutes and {seconds} seconds."
        response = dict(error=error_message)
        return response
    return None


async def update_failed(failed_logins, email):
    now = datetime.datetime.now()
    response = dict(error="wrong password!")
    if email in failed_logins.keys():
        if len(failed_logins[email]) <= 2:
            failed_logins[email].append(now)
        else:
            since_first = now - failed_logins[email][0]
            if since_first <= datetime.timedelta(seconds=60):
                response = dict(error="Wrong Password for the third time. Please wait five Minutes to retry.")
                failed_logins[email].append(now)
    else:
        failed_logins[email] = [now]
    return response, failed_logins

async def login(request):
    try:
        data = dict(email=request['data']['email'], logged_in=True)
        is_retry = data['email'] in request.app['failed_logins'].keys()
        if is_retry:
            response = await check_retries(request.app['failed_logins'], data['email'])
            if response:
                return web.json_response(response, status=401)
        account = await Account().update(request['connection'], key='email', data=data)
        password_is_correct = pbkdf2_sha512.verify(
                request['data']['password'], account['password']
                )
        if password_is_correct:
            del account['password']
            payload = dict(email=account['email'], id=account['id'])
            token = await create(payload=payload)
            acc_serialized = await serialize('accounts', account)
            response = {
                'account': acc_serialized,
                'message': 'successfully logged in'
                }
            headers = {
                'AUTH-TOKEN': token
                }
            return web.json_response(response, headers=headers)
        else:
            response, request.app['failed_logins'] = await update_failed(request.app['failed_logins'], data['email'])
            return web.json_response(response, status=401)
    except TypeError:
        response = dict(error=f"account with email {data['email']} does not exist")
        return web.json_response(response, status=401)


async def token_login(request):
    data = {'id': request['account']['id'], 'logged_in': True}
    request['account'] = await Account().update(request['connection'], data=data)
    token = await create(
            payload=dict(id=request['account']['id'], email=request['account']['email'])
            )
    acc_serialized = await serialize('accounts', request['account'])
    headers = {
        'AUTH-TOKEN': token
        }
    response = {
        'account': acc_serialized,
        'message': f"welcome back {request['account']['email']}!"
        }
    return web.json_response(response, headers=headers)


async def logout(request):
    data = {'id': request['account']['id'], 'logged_in': False}
    await Account().update(request['connection'], data=data)
    response = {
        'message': f"{request['account']['email']} successfully logged out."
        }
    return web.json_response(response)
