import logging
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from bonham.root import init_app


class TestRoot(AioHTTPTestCase):
    async def get_application(self, loop):
        app = await init_app(loop=loop)
        return app

    @unittest_run_loop
    async def test_app(self):
        assert self.app.logger == logging.getLogger('bonham.root')
        assert all(key in self.app.keys() for key in
                   ['server', 'handler', 'db', 'wss', 'auth_users', 'aiohttp_jinja2_environment'])

    @unittest_run_loop
    async def test_app_index(self):
        response = await self.client.get('/')
        assert response.status == 200
        assert b'<!DOCTYPE html>' in await response.content.read()
