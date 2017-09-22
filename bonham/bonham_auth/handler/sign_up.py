from aiohttp import web
from asyncpg import UniqueViolationError

from bonham.bonham_auth.models import Account
from bonham.bonham_auth.token import create_token
from bonham.bonham_auth.validators import is_valid_sign_up_data
from bonham.bonham_core.exceptions import RequestDenied
from bonham.bonham_core.serializer import serialize

__all__ = ('sign_up',)

async def sign_up(request: web.Request) -> web.json_response:
    """
    flow:
        -> check if email and password are present and valid
        -> create account and save to db
        -> create response object
    """
    try:

        await is_valid_sign_up_data(request['data'])

        async with request['connection'].transaction():

            account = await Account(**request['data']).create(
                request['connection'], returning=['_id', 'email', 'created'])
            payload = dict(email=account['email'], id=account['_id'])
            access_token = await create_token(payload)
            message = f"We send an email to {account['email']} " \
                      f"with a link to finish the sign up process."
            response = dict(
                message=message,
                data=await serialize('accounts', account)
                )
            headers = dict(access=access_token)
            return web.json_response(response, headers=headers)

    except (ValueError, UniqueViolationError):

        return web.json_response(dict(
            error=f"account with email {request['data']['email']} "
                  f"already exists."
            ), status=405)

    except RequestDenied as e:

        return web.json_response(dict(error=str(e)), status=405)
