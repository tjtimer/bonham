# bonham test_app_setup
# created: 27.06.18
# Author: Tim "tjtimer" Jedro
# Email: tjtimer@gmail.com

from vibora import TestSuite
from pprint import pprint

from bonham.app import app


class HomeTestCase(TestSuite):
    def setUp(self):
        self.client = app.test_client()

    async def test_index(self):
        response = await self.client.get('/')
        pprint(dir(response))
        self.assertEqual(response.content, b'index response')

    async def test_static(self):
        response = await self.client.get('/s/')
        pprint(response)
        self.assertEqual(response.content, b'security index response')
