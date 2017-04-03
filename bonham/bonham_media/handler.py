from aiohttp import web

from bonham.bonham_media.models import Gallery, GalleryEditor


async def create_gallery(request):
    gallery = Gallery(**request['data']['gallery'])
    try:
        await gallery.create(connection=request['connection'])
        await GalleryEditor(
                account_id=request['account']['id'],
                gallery_id=gallery['id']).create(connection=request['connection'])
        gallery_serialized = await gallery.serialized()
        return web.json_response(dict(gallery=gallery_serialized))
    except Exception as e:
        print(f"Exception at create_gallery handler:\n\t{type(e).__name__}: {e}")
        raise


async def get_galleries(request):
    gallery = Gallery()
    try:
        galleries = await gallery.get(connection=request['connection'])
        galleries_serialized = [await Gallery(**gallery_data).serialized() for gallery_data in galleries]
        return web.json_response(dict(galleries=galleries_serialized))
    except Exception as e:
        print(f"Exception at get_galleries\n\t{type(e).__name__}: {e}\n")
        raise
