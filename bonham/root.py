from argparse import ArgumentParser
import asyncio
from asyncio import wait

from aiohttp import web
import aiohttp_jinja2
import arrow
import jinja2
import sys
from uvloop import EventLoopPolicy

from bonham import db, logger, middlewares, router
from bonham.bonham_authentication import root as auth
from bonham.bonham_authentication.models import *
from bonham.bonham_calendar import root as calendar
from bonham.bonham_media.models import *
from bonham.bonham_profile.models import *
from bonham.bonham_tag import root as tags
from bonham.bonham_tag.models import *
from bonham.settings import DEBUG, TEMPLATE_DIR
from bonham.utils import prepared_uvloop

# use uvloop
asyncio.set_event_loop_policy(EventLoopPolicy())

core_setup = [db, router, logger]

components = [auth, calendar, tags]

tables = db.create_tables(models=[
    Account,
    AccessToken,
    Group,
    GroupAdmin,
    GroupEditor,
    User,
    GGConnection,
    GUConnection,
    UUConnection,
    Gallery,
    GalleryAdmin,
    GalleryEditor,
    Picture,
    PictureAdmin,
    PictureEditor,
    GalleryPicture,
    Tag,
    TaggedItem
    ])


async def setup_core(app):
    tasks = [app.loop.create_task(component.setup(app)) for component in core_setup]
    await wait(tasks)
    return app


async def setup_components(app):
    tasks = [app.loop.create_task(component.setup(app)) for component in components]
    await wait(tasks)
    return app


async def prepare_response(request, response):
    sys.stdout.write(f"prepare-response called!\n{response}\n{request}", flush=True)
    response.charset = 'utf-8'
    response.cookies.clear()


async def shutdown(application: web.Application):
    print(f"Bonham App Server shutdown() called at {arrow.now()}.")
    if application:
        for component in components:
            await component.shutdown(application)
        await application['db'].close()
        application['server'].close()
        await application['server'].wait_closed()
        await application['handler'].shutdown(60)
        await application.cleanup()
    return


async def startup(application: web.Application) -> None:
    print(f"root startup()\n\twith admins: {application['admins']}", flush=True)


async def init_app(*, loop: asyncio.BaseEventLoop = None, port: int = None) -> web.Application:
    app = web.Application(middlewares=middlewares.all, loop=loop, debug=DEBUG)
    app['wss'] = {}
    app['tables'] = [t.name for t in Base.metadata.sorted_tables]

    # setup aiohttp_jinja2 template_engine
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(TEMPLATE_DIR))

    # parrallel setup of components
    await setup_core(app)
    await setup_components(app)

    app['handler'] = app.make_handler(
            secure_proxy_ssl_header=('X-FORWARDED-PROTO', 'https'),
            slow_request_timeout=20)

    app['server'] = await loop.create_server(app['handler'], '127.0.1.2', port)
    await startup(app)
    print(f"\n\n{'*'*10} Bonham App Server - port {port} {'*'*10}\n\n", flush=True)
    return app


def main():
    parser = ArgumentParser('Run a Bonham App Server instance on specified port.')
    parser.add_argument('--development', '-d', action='store_true',
                        help='if passed loop will not be closed.')
    parser.add_argument('port', type=int,
                        help='port number for this server instance , type: int (e.g 8080)')
    args = parser.parse_args()
    if args.port is None:
        args.port = int(input("choose a port:"))
    loop = prepared_uvloop(debug=DEBUG)
    sys.stdout.write(f"\nrunning in development mode: {args.development}\n")
    app = loop.run_until_complete(init_app(loop=loop, port=args.port))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        sys.stdout.write("\n\nKeyboardInterrupt at Bonham App Server.\n\n")
        pass
    except:
        pass
    finally:
        sys.stdout.write(f"\n\n{'*'*10} Shutting down Bonham App Server instance on port {args.port} {'*'*10}\n\n")
        loop.run_until_complete(shutdown(app))
        if not args.development:
            sys.stdout.write(f"stop and close loop")
            loop.stop()
            loop.close()
        sys.stdout.write(f"Successfully shut down Bonham App Server instance.")


if __name__ == '__main__':
    main()
