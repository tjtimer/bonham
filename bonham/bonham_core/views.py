from aiohttp import web
from aiohttp_jinja2 import template

from bonham.settings import APPLICATION_NAME

__all__ = ['index', 'ping']

async def get_context(request):
    user_agent = request.headers.pop('User-Agent')
    print(f"user-agent: {user_agent}")
    return dict(
            title=APPLICATION_NAME,
            lang='de_DE'
            )


@template('index.html')
async def index(request):
    print(f"request at index:\n\t{vars(request)}")
    return await get_context(request)


@template('swagger.html')
async def swagger_api(request):
    return {}

async def ping(request)-> web.Response:
    """
    ---
    description: This end-point allow to test that service is up.
    tags:
    - Health check
    produces:
    - text/plain
    responses:
        "200":
            description: successful operation. Return "pong" text
        "405":
            description: invalid HTTP Method
    """
    print(vars(request))
    return web.Response(text="pong")
