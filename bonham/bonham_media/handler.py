from aiohttp import web

from bonham.bonham_media.models import Gallery, GalleryEditor
from bonham.serializer import serialize


async def create_gallery(request):
    gallery = Gallery()
    try:
        await gallery.create(connection=request['connection'], data=request['data']['gallery'])
        await GalleryEditor().create(connection=request['connection'], data=dict(account_id=request['account']['id'],
                                                                                 gallery_id=gallery['id']))
        gallery_serialized = await serialize('galleries', gallery)
        return web.json_response(dict(gallery=gallery_serialized))
    except Exception as e:
        print(f"Exception at create_gallery handler:\n\t{type(e).__name__}: {e}")
        raise


async def get_galleries(request):
    gallery = Gallery()
    try:
        galleries = await gallery.get(connection=request['connection'])
        galleries_serialized = await serialize('galleries', galleries)
        return web.json_response(galleries_serialized)
    except Exception as e:
        print(f"Exception at get_galleries\n\t{type(e).__name__}: {e}\n")
        raise
