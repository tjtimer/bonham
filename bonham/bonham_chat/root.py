"""
Name: bonham - root 
Author: Tim "tjtimer" Jedro
Email: tjtimer@gmail.com
Version: 0.0.1dev

created: 21.09.17 09:57
"""

import logging

from bonham.bonham_core.component import Component

__all__ = ()

logger = logging.getLogger(__name__)


class Chat(Component):
    r"""Chat component
    handles multiple websockets to provide chat capability.
    """

    def __init__(self,
                 service, *,
                 max_msg_size=2048 ** 2):
        self.max_msg_size = max_msg_size
        super().__init__(service)

    async def setup(self):
        pass

    async def shutdown(self):
        pass
