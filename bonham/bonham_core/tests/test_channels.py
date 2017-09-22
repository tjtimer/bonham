"""
Name: bonham test_channels 
Author: Tim "tjtimer" Jedro
Email: tjtimer@gmail.com
Version: 

16.08.17 13:43
"""
import asyncio
import unittest
from asyncio.test_utils import TestCase

from bonham.bonham_core.channels import Channel
from bonham.bonham_core.helper import BLoop

__all__ = ()

import logging

logger = logging.getLogger(__name__)


class TestChannel(TestCase):
    def setUp(self):
        self.loop = BLoop()
        self.set_event_loop(self.loop)
        self.channel = Channel()
        self.subscriber_1 = asyncio.Queue()
        self.subscriber_2 = asyncio.Queue()
        self.subscriber_3 = asyncio.Queue()

    def tearDown(self):
        self.loop.stop()
        self.loop.close()

    def test_channel_can_register_listener(self):
        assert len(self.channel.audience) is 0
        self.loop.run_until_complete(self.channel.subscribe(self.subscriber_1))
        assert len(self.channel.audience) is 1


if __name__ == '__main__':
    unittest.main()
