from aiohttp import web



from ..app import routes

@routes.put('/activate/{activation}')
async def activate(request):
    #  TODO: get account data as it is not send with the header (user clicked link in activation email)
    request['account'] = Account(activation_key=request.match_info['activation_key']).update(
            request['connection'], ref='activation_key', data=dict(activation_key='0'), returning=['id'])
    access_token = await create_token(request)
    response = dict(
            message="You're account was successfully activated."
            )
    headers = {
        'access': access_token
        }
    return web.json_response(response, headers=headers)
