from aiohttp import web

from bonham.bonham_auth.decorators import authentication_required
from bonham.bonham_auth.models import Account
from bonham.bonham_core.decorators import db_connection


@authentication_required
@db_connection
async def logout(request):
    account = Account(
        request['connection'], id=request['token_data']['id']
        )
    await account.update(data=dict(
            logged_in=False
        ))
    response = web.json_response(dict(message=f"Successfully logged out."))
    response.del_cookie('bearer')
    return response
