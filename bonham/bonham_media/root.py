from aiohttp import web

from bonham.bonham_media.handler import create_gallery, get_galleries


async def setup_routes(router):
    router.add_get('/', get_galleries)
    router.add_post('/', create_gallery)


async def setup(app):
    media = web.Application(loop=app.loop)
    await setup_routes(media)
    app.add_subapp('/media', media)
