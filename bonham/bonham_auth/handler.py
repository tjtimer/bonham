from asyncio import gather

import arrow
from aiohttp import web
from asyncpg import UniqueViolationError
from passlib.hash import pbkdf2_sha512

from bonham import db
from bonham.errors import RequestDenied
from bonham.serializer import serialize
from .models import Account, RefreshToken, validate_data
from .token import *

__all__ = ['sign_up', 'login', 'logout', 'token_login', 'activate']


async def sign_up(request):
    account = None
    try:
        if await validate_data(request['data']):
            async with request['connection'].transaction():
                account = await Account(request['data']).create(request['connection'],
                                                                returning=['id', 'email', 'created'])
                payload = dict(email=account['email'], id=account['id'])
                token = await create_access_token(payload=payload)
                message = f"We send an email to {account['email']} with a link to finish the sign up process."
                response = dict(message=message, data=await serialize('accounts', account))
                headers = dict(access=token)
                return web.json_response(response, headers=headers)
        else:
            return web.json_response({'error': 'Invalid email and/or password!'}, status=400)
    except (ValueError, UniqueViolationError):
        return web.json_response({
            'error': f"account with email {request['data']['email']} already exists."
            }, status=400)
    finally:
        if account:
            await request.app['root'].on_account_created.send(account)


async def check_password(req_pass, db_pass):
    if not pbkdf2_sha512.verify(req_pass, db_pass):
        raise RequestDenied('wrong password')
    return


async def check_retries(email, failed_logins):
    is_retry = email in failed_logins.keys()
    if is_retry:
        now = arrow.now()
        if len(failed_logins[email]) >= 3 and failed_logins[email][-1].replace(minutes=1) <= now:
            wait_until = now.replace(minutes=5)
            error_message = f"To many failed retries. Please wait until {wait_until}."
            raise RequestDenied(error_message)
    return


async def update_failed(email, failed_logins):
    now = arrow.now()
    response = dict(error="wrong password!")
    if email in failed_logins.keys():
        if len(failed_logins[email]) <= 2:
            failed_logins[email].append(now)
        else:
            if now <= failed_logins[email][0].replace(seconds=90):
                response = dict(error="Wrong Password for the third time. Please wait five Minutes to retry.")
                failed_logins[email].append(now)
    else:
        failed_logins[email] = [now]
    return response, failed_logins

async def login(request: web.Request) -> web.json_response:
    """
    flow:
        - read email from request['data']
        - check retries
            -> refuse request if user failed to log in more than:
                - 3 times in 60 seconds
                - more than 20 times in 60 minutes
        - get account data from db
        - check password
            -> if password is wrong
                - refuse request
                - add email-address, user agent and timestamp to failed logins
        - update account data (set is_logged_in to True and save to db)
        - create access, bearer and refresh token
        - save refresh and bearer token to db
        - create json response from success message
        - add access and refresh token to response.headers
        - add bearer token cookie to response.cookies
        - return response

    :param request: contains data and app, necessary to perform login
    :type request: aiohttp.web.Request
    :return: response object containing cookies, headers and message
    :rtype: aiohttp.web.json_response
    """
    try:
        await check_retries(request['data']['email'], request.app['failed_logins'])
        account = await Account(
                email=request['data']['email']
                ).get_by_key(
                request['connection'],
                key='email', returning=['id', 'email', 'password']
                )
        await check_password(request['data']['password'], account['password'])
        await Account(
                id=account['id'], logged_in=True
                ).update(
                request['connection'],
                returning=['id']
                )
        access_token = await create_access_token(request)
        refresh_token = await RefreshToken(
                owner=account['id']
                ).get_by_key(
                request['connection'], key='owner'
                )
        response = web.json_response(
                dict(message=f"welcome back {request['data']['email']}."),
                headers=dict(access=access_token, bearer=refresh_token['token'])
                )
        max_age = 2400 * 3600  # 100 days
        response.set_cookie('bearer', str(refresh_token['token']),
                            max_age=max_age, secure=True, httponly=True)
        return response
    except KeyError as e:
        return web.json_response(dict(error=f"Request must provide {e}."))
    except TypeError:
        return web.json_response(dict(error=f"account with email {request['data']['email']} does not exist"), status=401)
    except RequestDenied as e:
        return web.json_response(dict(error=e), status=401)


async def token_login(request):
    success = False
    try:
        account, token = await gather(
                Account(id=request['account']['id'], logged_in=True).update(request['connection'], returning=['id']),
                create_access_token(request)
                )
        refresh_token = await RefreshToken(
                owner=request['account']['id']
                ).get_by_key(
                request['connection'],
                key='owner', value=request['account']['id'], returning=['token'])
        headers = dict(access=token, bearer=refresh_token['token'])
        response = dict(message=f"welcome back {request['account']['email']}!")
        success = True
        response = web.json_response(response, headers=headers)
        max_age = 15 * 3600  # 15 minutes
        response.set_cookie('bearer', str(refresh_token['token']),
                            max_age=max_age, secure=True, httponly=True)
        return response
    finally:
        if success:
            await request.app['root'].on_account_logged_in.send(request['account']['id'])


async def logout(request):
    data = dict(
            id=request['account']['id'],
            logged_in=False
            )
    await db.update(request['connection'], 'account', data=data)
    response = web.json_response(dict(message=f"Successfully logged out."))
    response.del_cookie('bearer')
    return response


async def activate(request):
    #  TODO: get account data as it is not send with the header (user clicked link in activation email)
    request['account'] = Account(activation_key=request.match_info['activation_key']).update(
            request['connection'], ref='activation_key', data=dict(activation_key='0'), returning=['id'])
    token = await create_access_token(request)
    response = dict(
            message="You're account was successfully activated."
            )
    headers = {
        'access': token
        }
    return web.json_response(response, headers=headers)
