"""

 config
"""
import os
import socket

from bonham.core.utils import opj


__all__ = ('load_config', 'ApplicationConfig')

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

def parse_directories(config):
    root_directory = config.pop('root_directory', os.getcwd())
    application = config.pop('application_root','application')
    if not application.startswith('/'):
        application = opj(root_directory, application)
    public = config.pop('public_root', 'public')
    if not public.startswith('/'):
        public = opj(root_directory, public)
    templates = config.get('templates_dir', 'templates')
    if config.get('template_loader', 'system') == 'system':
        if not templates.startswith('/'):
            templates = opj(application, templates)
    directories = dict(
        root=root_directory,
        public=public,
        application=application,
        templates=templates,
        apps=config.get('apps_dir', 'apps'),
        static = opj(public, config.pop('static_dir', 'static')),
        media = opj(public, config.pop('media_dir', 'media')),
        certificates = opj(application, '.certificates'),
        secrets = opj(application, '.secrets'),
        sockets = opj(application, '.scks'),
        conf = opj(application, 'conf'),
        log = opj(application, 'log'),
        tmp = opj(application, 'tmp')
    )
    return directories

class ApplicationConfig:
    __slots__ = (
        'name', 'debug', 'log', 'directories', 'ssl',
        'template_loader', 'replica', 'databases', 'auth_enabled'
    )

    def __init__(self, conf_path: str):
        raw_conf = load_config(conf_path)
        debug = raw_conf.pop('debug', False)
        debug_env = raw_conf.pop('debug_env', None)
        if debug_env is not None:
            debug = debug and socket.gethostname() in debug_env
        self.debug = debug
        self.name = raw_conf.pop('name', 'application')
        self.directories = parse_directories(raw_conf)
        log = raw_conf.pop('logging_config', None)
        if isinstance(log, dict):
            if 'path' in log.keys() and not log['path'].startswith('/'):
                log['path'] = opj(
                    self.directories['conf'],
                    log['path'])
        elif isinstance(log, str) and not log.startswith('/'):
            log = opj(self.directories['conf'], log)
        self.log = log
        self.ssl = raw_conf.pop('ssl', False)
        self.replica = raw_conf.pop('replica', 1)
        self.template_loader = raw_conf.pop('template_loader', 'system')
        self.auth_enabled = raw_conf.pop('auth')

        local_conf = raw_conf.get('local_conf', False)
        if local_conf is not False:
            if not local_conf.startswith('/'):
                local_conf = opj(self.directories['conf'], local_conf)
            local_conf = load_config(local_conf)
            self.__dict__.update(**local_conf)



    def __getitem__(self, item):
        return self.__getattribute__(item)
