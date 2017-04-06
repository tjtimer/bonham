from asyncio import ensure_future, wait

from aiohttp import web
import sys

from bonham import db
from bonham.settings import ADMIN
from .handler import login, logout, sign_up, token_login
from .middlewares import auth_middleware
from .models import Account


async def authentication_required_response():
    response = dict(error=f"Please log in or sign up to proceed.")
    return web.json_response(response, status=401)


async def setup_routes(router):
    router.add_post('/sign-up/', sign_up, name='sign-up')
    router.add_put('/login/', login, name='login')
    router.add_put('/token-login/', token_login, name='token-login')
    router.add_put(r'/logout/', logout, name='logout')


async def setup_admins(app):
    async with app['db'].acquire() as connection:
        async with connection.transaction():
            where = f"is_superuser IS TRUE"
            admins = list(await db.get(connection, table=Account.__table__, where=where))
            app['admins'] = {admin['id']: {'id': admin['id'], 'email': admin['email']} for admin in admins}
            if not len(app['admins']):
                acc_data = ADMIN
                admin = await db.create(connection, table=Account.__table__, data=acc_data)
                app['admins'][admin['id']] = admin

async def shutdown(app):
    sys.stdout.write(f"shutting down Authentication!\n")


async def setup(app):
    print(f"Authentication setup", flush=True)
    auth = web.Application(loop=app.loop)
    await wait([
        ensure_future(setup_admins(app)),
        ensure_future(setup_routes(auth.router)),
        ])
    app.middlewares.append(auth_middleware)
    auth['failed_logins'] = {}
    auth['authenticated_accounts'] = set()
    return app.add_subapp('/auth', auth)
