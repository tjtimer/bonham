from collections import namedtuple

import aiofiles

__all__ = [
    'read',
    'setup',
    'default_channels'
    ]

listener = namedtuple('listener', ['id', 'queue'])

default_channels = []


class Channel(object):

    def __init__(self, name: str=None):
        self.name = name


    def add_listener(self, listener: listener):
        self.listner.add(listener)


    async def read(file_name: str=None):
        if file_name is None:
            file_name = 'bonham/MESHUGGAH-the-violent-sleep-of-reason-cover.png'
        async with aiofiles.open(file_name, mode='rb') as in_file:
            async for chunk in in_file:
                print('chunk: ', chunk.decode())
            print('finished reading')
        print('closed file')
