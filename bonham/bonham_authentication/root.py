from asyncio import ensure_future, wait

from aiohttp import web
from asyncpg import UniqueViolationError

from bonham.bonham_authentication.handler import login, logout, sign_up, token_login
from bonham.bonham_authentication.middlewares import auth_middleware
from bonham.bonham_authentication.models import Account
from bonham.settings import ADMIN


async def setup_routes(router):
    router.add_post('/sign-up/', sign_up, name='sign-up')
    router.add_put('/login/', login, name='login')
    router.add_put('/token-login/', token_login, name='token-login')
    router.add_put(r'/logout/', logout, name='logout')


async def setup_superuser(app):
    acc_data = ADMIN
    async with app['db'].acquire() as connection:
        app['admin'] = Account(**acc_data)
        try:
            await app['admin'].create(connection=connection)
            app.logger.debug(f"Superuser created: {app['admin']}")
        except UniqueViolationError:
            admin_data = list(await app['admin'].get(connection=connection, where=f"is_superuser IS TRUE"))[0]
            app['admin'] = Account(**admin_data)
            app.logger.debug(f"Superuser exists: {app['admin']}")


async def on_startup(app):
    print(f"authentication on_startup: app: {app}")


async def shutdown(app):
    print(f"shutdown authentication.")


async def setup(app):
    auth = web.Application()
    await wait([
        ensure_future(setup_routes(auth.router)),
        ensure_future(setup_superuser(app))
        ])
    auth.on_startup.append(on_startup)
    app.middlewares.append(auth_middleware)
    app['auth_users'] = {}
    app.add_subapp('/auth', auth)
