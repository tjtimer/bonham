"""
Name: bonham test_root 
Author: Tim "tjtimer" Jedro
Email: tjtimer@gmail.com
Version: 

27.08.17 21:59
"""
import asyncio
from asyncio.test_utils import TestCase

__all__ = ()

import logging

logger = logging.getLogger(__name__)


class TestMediaRoot(TestCase):
    def setUp(self):
        self._loop = asyncio.get_event_loop()
