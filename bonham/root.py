from argparse import ArgumentParser
import asyncio
from asyncio import Task, wait

from aiohttp import web
import aiohttp_jinja2
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

core_setup = [router, logger, db]

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
    return await wait(tasks)


async def setup_components(app):
    tasks = [app.loop.create_task(component.setup(app)) for component in components]
    await wait(tasks)
    return app


async def prepare_response(request, response):
    response.charset = 'utf-8'
    response.cookies.clear()


async def cancel_tasks():
    for task in Task.all_tasks():
        task.cancel()


async def shutdown(application: web.Application):
    print(f"shutdown app called.")
    if application:
        for component in components:
            await component.shutdown(application)
        await application['db'].close()
        application['server'].close()
        await application['server'].wait_closed()
        await application['handler'].shutdown(60)
        await cancel_tasks()
        await application.cleanup()


async def startup(application: web.Application) -> None:
    print(f"bonham -> root -> startup() called.\n\tadmins: {application['admins']}", flush=True)

async def init_app(loop: asyncio.BaseEventLoop = None, port: int = None) -> web.Application:
    app = web.Application(middlewares=middlewares.all, loop=loop, debug=DEBUG)
    app.on_startup.append(startup)
    # app.on_shutdown.append(shutdown)
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
    app.logger.info(f"server running on port {port}\nserver: {app['server']}\nhandler: {app['handler']}")
    return await app.startup()


def main():
    parser = ArgumentParser('Run a Bonham app instance on specified port.')
    parser.add_argument('--port', '-p', type=int,
                        help='port number for this server instance, type integer e.g 8000')
    args = parser.parse_args()
    if args.port is None:
        args.port = int(input("choose a port:"))
    loop = prepared_uvloop(debug=DEBUG)
    app = loop.run_until_complete(init_app(loop=loop, port=args.port))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        sys.stdout.write("\n\nKeyboardInterrupt at bonham root\n\n")
        pass
    except Exception as e:
        sys.stdout.write(f"\n\n#########\nException at bonham root\n\n{type(e).__name__}")
        pass
    finally:
        sys.stdout.write(f"\n\n{'*'*10} Shutting down bonham app instance on port {args.port} {'*'*10}\n\n")
        loop.run_until_complete(shutdown(app))
        loop.stop()
        loop.close()
        sys.stdout.write(f"Successfully shut down bonham app instance.")


if __name__ == '__main__':
    main()
