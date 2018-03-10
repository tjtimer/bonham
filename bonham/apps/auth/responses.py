"""

 responses
"""
from aiohttp import web


async def authentication_required_response():
    response = dict(error=f"Please log in or sign up to proceed.")
    return web.json_response(response, status=401)

