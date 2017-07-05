from aiohttp import web

from bonham.bonham_core import db


async def logout(request):
    data = dict(
            id=request['account']['id'],
            logged_in=False
            )
    await db.update(request['connection'], 'account', data=data)
    response = web.json_response(dict(message=f"Successfully logged out."))
    response.del_cookie('bearer')
    return response
