
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
import asyncio
import time

import arrow
from aiohttp import web

from bonham.apps.auth import create_token
from .functions import setup_admins
from .models import *


__all__ = ('models', 'routes', 'on_startup')

routes = web.RouteTableDef()
models = (Account, RefreshToken, Role, Permission)
on_startup = setup_admins



async def setup_admins(app):
    app['admins'] = dict()
    async with app['pg_db'].acquire() as connection:
        admins = await Account(is_superuser=True).get(
            connection, returning=['id', 'email']
        )
        if not admins:
            admins_data = [
                {'is_superuser': True,
                 'is_verified': True,
                 'email': 'admin@email.com',
                 'password': 'totallySecure!'}]
            admins = await asyncio.gather(
                *(Account().create(
                    connection,
                    data=data,
                    returning=['id', 'email', 'created']
                    ) for data in admins_data)
                )
            print(admins)
            for admin in admins:
                ref_token = await create_token(
                        {
                            'id': admin['id'],
                            'idc': arrow.get(admin['created']).format('X'),
                            'clientId': f"{admin['email'].split('@')[0]}.{time.time()}"
                        },
                        app['config']
                    )
                await RefreshToken().create(
                            connection,
                            data=dict(owner=admin['id'], token=ref_token),
                            returning=['id']
                )
                app['admins'][admin['id']] = admin
        else:
            app['admins'] = {admin['id']: admin for admin in admins}
    return app
