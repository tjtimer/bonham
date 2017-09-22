"""
Name: bonham root 
Author: Tim "tjtimer" Jedro
Email: tjtimer@gmail.com
Version: 

27.08.17 18:25
"""
from bonham.bonham_core.component import Component

__all__ = ()

import logging

logger = logging.getLogger(__name__)


class Media(Component):
    async def setup(self, service):
        r"""Setup Media"""

    async def shutdown(self, service):
        r"""Shutdown Media"""
