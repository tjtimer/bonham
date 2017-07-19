
"""
    Bonham Auth
    Author: Tim "tjtimer" Jedro
    Email: tjtimer@gmail.com
    Version: 0.0.1dev
    Auth flow:
        - user creates account / signs up with email and password
        - user gets mail with link containing the activation key
        - user clicks link in mail
        - account gets activated and user gets logged in
        - login:
            -> create refresh token and save to db (used to create new access token)
            -> set cookie with refresh token (used on page request)
            -> create access token (used for API requests; don't save anywhere)
            -> set header with refresh token and access token
        - logout:
            -> delete cookie that holds the refresh token
            -> delete refresh token from db
"""

import logging
import time
from asyncio import gather

import arrow
from aiohttp import web

from bonham.bonham_auth.token import create_token
from bonham.settings import ADMINS
from .handler import activate, login, logout, sign_up
from .models import *

__all__ = ['setup', 'shutdown', 'setup_routes', 'setup_admins', 'authentication_required_response']


async def authentication_required_response():
    response = dict(error=f"Please log in or sign up to proceed.")
    return web.json_response(response, status=401)


async def add_tables(service):
    for model in [Account, RefreshToken]:
        service.tables[model.__table__] = model.__table__.c.keys()
    return service


async def setup_routes(router):
    router.add_post('/sign-up/', sign_up, name='sign-up')
    router.add_put('/login/', login, name='login')
    router.add_put(r'/logout/', logout, name='logout')
    router.add_get(r'/{activation_key}/', activate, name='activate')


async def setup_admins(service):
    service['admins'] = dict()
    async with service.db.acquire() as connection:
        admins = await Account(is_superuser=True).get(connection, returning=['id', 'email'])
        if not admins:
            admins_data = ADMINS
            for acc_data in admins_data:
                admin = await Account().create(connection,
                                               data=acc_data,
                                               returning=['id', 'email', 'created']
                                               )
                print(admin)
                ref_token_data = dict(
                        id=admin['id'],
                        idc=arrow.get(admin['created']).format('X'),
                        clientId=f"{admin['email'].split('@')[0]}.{time.time()}")
                ref_token = await create_token(ref_token_data)
                await RefreshToken().create(connection,
                                            data=dict(owner=admin['id'], token=ref_token),
                                            returning=['id'])
                service['admins'][admin['id']] = {'id': admin['id'], 'email': admin['email']}
        else:
            service['admins'] = {admin['id']: {'id': admin['id'], 'email': admin['email']} for admin in admins}
    return service


async def log_logged_in(account):
    logger = logging.getLogger('bonham.root')
    logger.debug(f"login success: {account}")


async def shutdown(service):
    print(f"Authentication shut down!")


async def setup(service):
    service.logger.debug(f"Authentication setup")
    # service.middlewares.append(access_middleware)  # must be part of the global middleware chain
    # service.middlewares.append(bearer_middleware)  # must be part of the global middleware chain
    auth = web.Application(loop=service.loop)
    await gather(
            add_tables(service),
            setup_admins(service),
            setup_routes(auth.router)
            )
    auth['root'] = service
    auth['failed_logins'] = {}
    auth['authenticated_accounts'] = set()
    service.add_subapp('/auth', auth)
