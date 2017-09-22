"""
Name: bonham  create 
Author: Tim "tjtimer" Jedro
Email: tjtimer@gmail.com
Version:  - 28.08.17 10:42 

"""

import logging

from aiohttp import web

from bonham.bonham_auth.decorators import authentication_required, db_connection
from bonham.bonham_core.decorators import load_data

__all__ = ()

logger = logging.getLogger(__name__)


@authentication_required
@load_data
@db_connection
async def create_gallery(request: web.Request) -> web.json_response:
    r"""create_gallery
    flow:
        - get profile id from request['token_data']
        - get data from request['data']
    """
    pass
