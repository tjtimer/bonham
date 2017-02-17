from aiohttp import web

from bonham.bonham_authentication.handler import login, logout, sign_up, token_login


def setup_routes(router):
    router.add_post('/sign-up/', sign_up, name='sign-up')
    router.add_put('/login/', login, name='login')
    router.add_put('/token-login/', token_login, name='token-login')
    router.add_put(r'/logout/', logout, name='logout')


app = web.Application()
setup_routes(app.router)
