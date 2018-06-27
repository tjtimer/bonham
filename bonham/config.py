# bonham config
# created: 27.06.18
# Author: Tim "tjtimer" Jedro
# Email: tjtimer@gmail.com
import os
import pathlib
import time

import yaml

BASE_DIR = pathlib.Path(os.getcwd())


class AppConfig(object):
    title: str
    version: str
    template_dir: str

    def __init__(self, **kwargs):
        self.__path = pathlib.Path(kwargs.get('path', BASE_DIR / 'conf' / 'app.conf.yaml'))
        self.title = kwargs.get('title', 'My App')
        self.version = kwargs.get('version', f'0.0.1.dev{time.time()}')
        self.template_dir = kwargs.get('template_dir', BASE_DIR / 'templates')
        if not self.__path.parent.exists():
            self.__path.parent.mkdir()
            self.save()
        self.load()

    #
    # def __getitem__(self, item):
    #     return self.__getattribute__(item)
    #
    # def __setitem__(self, key, value):
    #     return self.__setattr__(key, value)
    @property
    def data(self):
        return {k: str(v) for k, v in vars(self).items() if k in self.__annotations__.keys()}

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def save(self, path: str = None):
        if path is not None:
            self.__path = pathlib.Path(path)
        if not self.__path.parent.exists():
            self.__path.parent.mkdir()
        with open(self.__path, 'w') as f:
            f.write(yaml.serialize(**self.data))

    def load(self, path: str = None):
        if path is not None:
            self.__path = pathlib.Path(path)
        if not self.__path.exists():
            return self
        with open(self.__path, 'r') as f:
            data = yaml.safe_load(f)
            if data is not None:
                self.update(**data)
