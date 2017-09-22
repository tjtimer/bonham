from aiohttp import web
from aiohttp.web_request import Request
from aiohttp_jinja2 import render_template

from bonham.settings import HOST, SERVICE_NAME

__all__ = ['index', 'ping']

async def get_context(request):
    user_agent = request.headers.pop('User-Agent', None)
    print(f"user-agent: {user_agent}")
    return dict(
        title=HOST,
            lang='de_DE'
            )


async def index(request: Request):
    """
    Index documentation.

    ---
    description: This endpoint renders and serves index.html.
    tags:
    - Index
    produces:
    - text/html
    responses:
        "200":
            description: successful operation, returns index.html.
        "302":
            description: HTTPFound, returns index.html with redirect header
    """
    request.app.logger.debug(f"\n\nIndex request:\n\t{vars(request)}\n\n")
    response = render_template(
        'index.html', request,
        await get_context(request),
        app_key=f"{SERVICE_NAME}_jinja2_environment"
        )
    request.app.logger.debug(f"\n\nIndex response:\n\t{vars(response)}\n\n")
    return response


async def ping(_) -> web.Response:
    """
    ---
    description: This endpoint allow to test that service is up.
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
