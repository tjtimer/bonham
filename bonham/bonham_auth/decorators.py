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
    'check_bearer_token'
    )


def authentication_required(handler):
    """authentication_required decorator

    Injects 'token_data' into request object
    to be used in the decorated handler.

    Usage:
        @authentication_required
        async def my_handler(request):
            token_data = request['token_data']
            ...

    :raises RequestDenied exception if:
        - no access token in request.headers
        - access token has expired
    :returns response returned by handler
    """

    @wraps(handler)
    async def wrapped(request):
        access_token = request.headers.get('access', None)
        if access_token is None:
            return web.json_response(
                dict(error=f"request headers must provide an access token"),
                status=405
                )
        try:
            request['token_data'] = await verify_token(access_token)
            return await handler(request)
        except jwt.ExpiredSignatureError as ese:
            raise RequestDenied(f"{ese} -> access token expired")

    return wrapped
