from asyncio import ensure_future, wait

from aiohttp import web
import sys

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
    account = Account()
    app['admins'] = dict()
    async with app['db'].acquire() as connection:
        async with connection.transaction():
            where = f"is_superuser IS TRUE"
            admins = await account.get(connection, where=where)
            if not admins:
                acc_data = ADMIN
                admin = await account.create(connection, data=acc_data)
                app['admins'][admin['id']] = {'id': admin['id'], 'email': admin['email']}
            else:
                app['admins'] = {admin['id']: {'id': admin['id'], 'email': admin['email']} for admin in admins}
    return app

async def shutdown(app):
    sys.stdout.write(f"Authentication shut down!\n")


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
    app.add_subapp('/auth', auth)
    return app
