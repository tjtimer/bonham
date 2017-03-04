from bonham.bonham_authentication import token
from bonham.bonham_user.models import User


async def auth_middleware(app, handler):

    async def au_middleware_handler(request):
        auth_token = request.headers.get('AUTH-TOKEN')
        request['user'] = User()
        if auth_token:
            r_user = await token.verify_user(auth_token)
            request['user'].__dict__.update(**r_user)
            app.logger.debug(f'\n{request["user"]}\nrequest:\n\t{request.__dict__}')
        response = await handler(request)
        return response

    return au_middleware_handler
