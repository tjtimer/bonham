from aiohttp import web

from bonham.bonham_auth import *
from bonham.bonham_core import *


async def login(request: web.Request) -> web.json_response:
    """
    flow:
        - read email from request['data']
        - check retries
            -> refuse request if user failed to log in more than:
                - 3 times in 90 seconds
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
        await check_password(request, account['password'])
        await Account(
                id=account['id'], logged_in=True
                ).update(
                request['connection'],
                returning=['id']
                )
        access_token = await create_token(request)
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
