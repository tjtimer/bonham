import os
import time
from collections import namedtuple
from pathlib import Path

import arrow
from bonham.bonham_core.file_io import read_file

web_template = namedtuple('web_template', ['file_name', 'expiration_date'])


class Template(object):

    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.default_expiration_time = 60 * 60 * 24 #  should be one day in seconds
        print('template:', vars(self))

    async def load(self, template_name):
        return await read_file(os.path.join(self.templates_dir, template_name))


