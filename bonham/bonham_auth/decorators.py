"""
bonham/bonham_auth/decorators.py

Author: Tim "tjtimer" Jedro

Version: 0.0.1dev1

"""
from functools import wraps

import jwt
from aiohttp import web

from bonham.bonham_auth.token import verify_token
from bonham.bonham_core.exceptions import RequestDenied

__all__ = (
    'authentication_required',
    )


def authentication_required(handler):
    """authentication_required decorator

    Injects access token payload into request object
    to be used in the decorated handler.

    Usage:
        @authentication_required
        async def my_handler(request):
            access_token_payload = request['access_token']
            ...

    :raises RequestDenied exception if:
        - no access token in request.headers
        - access token has expired
    :returns response returned by handler
    """

    @wraps(handler)
    async def wrapper(request):
        try:
            request['access_token'] = await verify_token(request.headers[
                                                             'access'])
            return await handler(request)
        except jwt.ExpiredSignatureError as ese:
            raise RequestDenied(f"{ese} -> access token expired")
        except KeyError:
            return web.json_response(
                dict(error=f"request headers must provide an access token"),
                status=405
                )

    return wrapper
