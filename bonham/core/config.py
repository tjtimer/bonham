"""

 config
"""
import logging.config
import os
import socket
import sys
from pathlib import Path
from types import ModuleType

from bonham.core.ssl import get_ssl_context
from bonham.core.utils import opj


__all__ = ('ApplicationConfig', 'conf_to_settings', 'load_config')


def conf_to_settings(path: str or Path, *,
                     name: str = 'settings',
                     append: bool = False):
    conf = ApplicationConfig(path)
    settings = ModuleType('settings')
    for k, v in conf.__dict__.items():
        setattr(settings, k.upper(), v)
    if append is True:
        sys.modules[name] = settings
    return settings


def init_logging(config: str or dict):
    if isinstance(config, str):
        config = load_config(config)
        logging.config.dictConfig(config)
    elif isinstance(config, dict):
        if 'type' not in config.keys():
            logging.config.dictConfig(config)
        elif config['type'] == 'ini':
            logging.config.fileConfig(config['path'])
        else:
            logging.config.listen(config['port'], verify=True)

def load_config(path: str) -> dict:
    f_type = path.split('.')[-1].lower()
    with open(path, 'r') as f:
        if f_type in 'ymlyaml':
            import yaml
            return yaml.safe_load(f.read())
        elif f_type == 'json':
            import json
            return json.loads(f.read())
        elif f_type in ['cfg', 'ini']:
            import configparser
            config = configparser.ConfigParser()
            return config.read_file(open(path))
        else:
            raise TypeError('Config file must be yaml, json, cfg or ini.')


class ApplicationConfig:
    ROOT_DIR = None
    PUBLIC_DIR = None
    APPLICATION_DIR = None
    TEMPLATES_DIR = None
    APPS_DIR = None
    STATIC_DIR = None
    MEDIA_DIR = None
    CERTIFICATES_DIR = None
    SECRETS_DIR = None
    SOCKETS_DIR = None
    CONF_DIR = None
    LOG_DIR = None
    TEMP_DIR = None

    def __init__(self, conf_path: str):
        self._conf = load_config(conf_path)
        debug = self._conf.get('debug', False)
        debug_env = self._conf.get('debug_env', None)
        if debug_env is not None:
            debug = debug and socket.gethostname() == debug_env

        self.parse_directories()
        self.NAME = self._conf.get('name', 'application')
        self.DEBUG = debug
        self.USE_SSL = self._conf.get('use_ssl', False)
        if self.USE_SSL is not False:
            self.SSL_CONTEXT = get_ssl_context()
        else:
            self.SSL_CONTEXT = None
        self.ENABLE_AUTH = self._conf.get('enable_auth')
        log = self._conf.get('logging_config', None)
        if isinstance(log, dict):
            if 'path' in log.keys() and not log['path'].startswith('/'):
                log['path'] = opj(
                    self.CONF_DIR,
                    log['path'])
        elif isinstance(log, str) and not log.startswith('/'):
            log = opj(self.CONF_DIR, log)
        self.LOG = init_logging(load_config(log))
        self.REPLICA = self._conf.get('replica', 1)
        self.TEMPLATE_LOADER_TYPE = self._conf.get('template_loader', 'system').upper()
        local_conf = self._conf.get('local_conf', None)
        if local_conf is not None:
            if not local_conf.startswith('/'):
                local_conf = opj(self.CONF_DIR, local_conf)
            local_conf = load_config(local_conf)
            self.__dict__.update({k.upper(): v for k, v in local_conf.items()})

    def __getitem__(self, item):
        return object.__getattribute__(self, item.upper())

    def parse_directories(self):
        root_directory = self._conf.get('root_dir', os.getcwd())
        application = self._conf.get('application_root', 'application')
        if not application.startswith('/'):
            application = opj(root_directory, application)
        public = self._conf.get('public_root', 'public')
        if not public.startswith('/'):
            public = opj(root_directory, public)
        templates = self._conf.get('templates_dir', 'templates')
        if self._conf.get('template_loader', 'system') == 'system':
            if not templates.startswith('/'):
                templates = opj(application, templates)
        self.ROOT_DIR = root_directory
        self.PUBLIC_DIR = public
        self.APPLICATION_DIR = application
        self.TEMPLATES_DIR = templates
        self.APPS_DIR = self._conf.get('apps_dir', 'apps')
        self.STATIC_DIR = opj(public, self._conf.get('static_dir', 'static'))
        self.MEDIA_DIR = opj(public, self._conf.get('media_dir', 'media'))
        self.CERTIFICATES_DIR = opj(application, '.certificates')
        self.SECRETS_DIR = opj(application, '.secrets')
        self.SOCKETS_DIR = opj(application, '.scks')
        self.CONF_DIR = opj(application, 'conf')
        self.LOG_DIR = opj(application, 'log')
        self.TEMP_DIR = opj(application, 'tmp')
