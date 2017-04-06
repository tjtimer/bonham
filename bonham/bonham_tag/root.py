from asyncio import ensure_future, wait

from aiohttp import web

from bonham.bonham_tag.handler import create_tag, create_tagged_item, get_tags
from bonham.bonham_tag.models import Tag


async def setup_routes(router):
    router.add_post('/', create_tag, name='create-tag')
    router.add_get('/', get_tags, name='get-tags')
    router.add_post('/{tag_name}/', create_tagged_item, name='create-tagged-item')
    #  router.add_get('/{tag_name}/', get_tagged_items, name='get-tagged-items')
    #  router.add_put('/{tag_id}/', update_tag, name='update_tag')
    #  router.add_delete('/{tag_id}/', delete_tag, name='delete-tag')


async def shutdown(app):
    print(f"Tag shut down!\n")

async def setup(app):
    tags = web.Application(loop=app.loop)
    tags['tables'] = app['tables'].append(Tag.metadata.sorted_tables)
    await wait([
        ensure_future(setup_routes(tags.router))
        ])
    app.add_subapp('/tags', tags)
    return app
