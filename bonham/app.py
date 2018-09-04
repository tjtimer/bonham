# bonham app
# created: 27.06.18
# Author: Tim "tjtimer" Jedro
# Email: tjtimer@gmail.com
#
# try:
#     import uvloop
#     import asyncio
#
#     asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
# except ImportError:
#     pass
import logging
from pprint import pprint
from vibora import Vibora, Request, Response
from vibora.static import StaticHandler

# components
from bonham.config import AppConfig

# services
from bonham.security.service import security

logger = logging.getLogger('app')
components = (AppConfig(),)
services = (
    (security, dict(security='/s')),
)


app = Vibora()

for comp in components:
    app.components.add(comp)

for service, prefix in services:
    app.add_blueprint(service, prefixes=prefix)


@app.route('/', methods=['GET'])
async def index(request: Request) -> Response:
    logger.debug(request.headers)
    return Response(b'app index')
