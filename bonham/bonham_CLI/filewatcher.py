"""
Name: bonham - filewatcher 
Author: Tim "tjtimer" Jedro
Email: tjtimer@gmail.com
Version: 0.0.1dev

created: 04.09.17 18:09
"""
import asyncio
import logging

__all__ = ()

logger = logging.getLogger(__name__)


# start here
class FileWatcher:

    def __init__(self):
        self._loop = asyncio.get_event_loop()
        self._file_changeds = asyncio.Event()
        self._transport = None
