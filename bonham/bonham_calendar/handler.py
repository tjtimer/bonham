from aiohttp import web


async def get_calendars(request):
    return web.json_response([])
