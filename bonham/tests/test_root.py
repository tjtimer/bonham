from asyncio.test_utils import TestCase
import logging

from bonham.root import init_app, shutdown
from bonham.utils import prepared_uvloop


class TestRoot(TestCase):
    def setUp(self):
        self.loop = prepared_uvloop(debug=True)
        self.app = self.loop.run_until_complete(init_app(loop=self.loop, port=9093))
        print(vars(self))

    def tearDown(self):
        print(vars(self))
        self.loop.run_until_complete(shutdown(self.app))
        self.loop.stop()
        self.loop.close()

    def test_app_logger(self):
        assert self.app.logger == logging.getLogger('bonham.log')
