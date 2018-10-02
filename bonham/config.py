# bonham config
# created: 27.06.18
# Author: Tim "tjtimer" Jedro
# Email: tjtimer@gmail.com
import os
import pathlib as pl
import time
import logging
from logging.config import dictConfig
import yaml

BASE_DIR: pl.Path = pl.Path(os.getcwd())

dictConfig({
    'version': 1,
    'formatters': {
        'detailed': {
            'class': 'logging.Formatter',
            'format': '%(asctime)s %(name)-15s %(levelname)-8s %(processName)-10s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',
            'level': 'DEBUG',
        },
        'dbg': {
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'detailed',
            'level': 'DEBUG',
            'mode': 'w'
        },
        'access': {
            'class': 'logging.FileHandler',
            'filename': 'access.log',
            'formatter': 'detailed',
            'mode': 'w'
        },
        'errors': {
            'class': 'logging.FileHandler',
            'filename': 'app-errors.log',
            'formatter': 'detailed',
            'level': 'ERROR',
            'mode': 'w'
        },
    },
    'loggers': {
        'bonham': {
            'handlers': ['console']
        },
        'config': {
            'handlers': ['console']
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'dbg', 'errors']
    },
})
logger = logging.getLogger('config')


class AppConfig:
    title: str
    version: str
    template_dir: pl.Path or str

    def __init__(self, **kwargs):
        self.__path = pl.Path(kwargs.get('path', BASE_DIR / 'conf' / 'app.conf.yaml'))
        self.title = kwargs.get('title', 'My App')
        self.version = kwargs.get('version', f'0.0.1.dev{time.time()}')
        self.template_dir = kwargs.get('template_dir', BASE_DIR / 'templates')
        try:
            self.load()
        except OSError:
            self.dump()
        finally:
            logger.debug(vars(self))

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def __setitem__(self, key, value):
        return self.__setattr__(key, value)

    @property
    def data(self):
        return {k: str(v) for k, v in vars(self).items() if k in self.__annotations__.keys()}

    @property
    def file(self):
        return self.__path

    @file.setter
    def file(self, path: pl.Path or str):
        _path = pl.Path(path)
        if not _path.parent.exists():
            _path.parent.mkdir()
        self.__path = _path

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def dump(self, path: pl.Path or str = None):
        if path is not None:
            self.file = path
        self.write()

    def write(self):
        with open(self.__path, 'w') as f:
            for k, v in self.data.items():
                f.write(f"{k}: {v}\n")

    def load(self, path: str = None):
        if path is not None:
            self.file = path
        if not self.__path.exists():
            logger.info(vars(self))
            return self
        with open(self.__path, 'r') as f:
            data = yaml.safe_load(f)
            if data not in [None, '']:
                self.update(**data)
