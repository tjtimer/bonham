from aiohttp import web

from bonham.bonham_auth.models import Account
from bonham.bonham_auth.token import create_token


async def activate(request):
    request['account'] = Account(activation_key=request.match_info['activation_key']).update(
            request['connection'], ref='activation_key', data=dict(activation_key='0'), returning=['id'])
    access_token = await create_token('access', request)
    response = dict(
            message="You're account was successfully activated."
            )
    headers = {
        'access': access_token
        }
    return web.json_response(response, headers=headers)
