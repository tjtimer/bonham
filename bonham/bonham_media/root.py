from aiohttp import web


async def setup_routes(router):
    router.add_get('/', get_)


async def setup(app):
    media = web.Application(loop=app.loop)
    await setup_routes(media)
