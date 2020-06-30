"""
bonham

app

Author: Tim "tjtimer" Jedro
Email: tjtimer@gmail.com
created: 30.06.20
"""
from pathlib import Path
from typing import Optional

from aiohttp import web

from bonham.core import config


class Bonham:
    def __init__(self, config_path: Optional[str or Path] = None):
        self._config = config.load(config_path)
        self._app = web.Application()
        
    @property
    def app(self):
        return self._app
    
    @property
    def config(self):
        return self._config
    
    def run(self):
        web.run_app(self._app, host=self._config.get('host', 'localhost'), port=self._config.get('port', 8080))
