from aiohttp import web
from asyncpg import UniqueViolationError

from bonham.bonham_auth import *
from bonham.bonham_core import *


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
                    request['connection'], returning=['id', 'email', 'created'])
            payload = dict(email=account['email'], id=account['id'])
            access_token = await create_token(payload)
            message = f"We send an email to {account['email']} with a link to finish the sign up process."
            response = dict(message=message, data=await serialize('accounts', account))
            headers = dict(access=access_token)
            return web.json_response(response, headers=headers)
    except (ValueError, UniqueViolationError):
        return web.json_response({
            'error': f"account with email {request['data']['email']} already exists."
            }, status=405)
    except RequestDenied as e:
        return web.json_response(dict(error=str(e)), status=405)
