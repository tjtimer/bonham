from aiohttp import web
from aiohttp_jinja2 import render_template

from bonham.settings import APPLICATION_NAME

__all__ = ['index', 'ping']

async def get_context(request):
    return dict(
            title=APPLICATION_NAME,
            lang='de_DE'
            )

async def index(request):
    context = await get_context(request)
    resp = render_template('index.html', request, context)
    print(resp)
    return resp


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
    return web.Response(text="pong")
