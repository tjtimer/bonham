from aiohttp import web

__all__ = ['invalid_data_response']


async def invalid_data_response(invalid):
    response = dict(error='invalid data',
                    data=invalid)
    return web.json_response(response, status=409)
