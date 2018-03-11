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
        else:
            raise TypeError('Config file must be yaml or json.')

def parse_directories(config):
    root_directory = config.pop('root_directory', os.getcwd())
    application = config.pop('application_root','application')
    if not application.startswith('/'):
        application = opj(root_directory, application)
    public = config.pop('public_root', 'public')
    if not public.startswith('/'):
        public = opj(root_directory, public)
    if config.get('template_loader', 'system') == 'system':
        templates = opj(application, 'templates')
    else:
        templates = 'templates'
    directories = dict(
        root=root_directory,
        public=public,
        static = opj(public, config.pop('static_dir', 'static')),
        media = opj(public, config.pop('media_dir', 'media')),
        application=application,
        templates=templates,
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
        debug = raw_conf.pop('debug', 'False').lower() in ['1', 'true', 'y', 'yes']
        debug_env = raw_conf.pop('debug_env', None)
        if debug_env is not None:
            debug = debug and socket.gethostname() in debug_env
        self.debug = debug
        self.name = raw_conf.get('name', 'application')
        self.directories = parse_directories(raw_conf)
        self.log = raw_conf.get('log_config', None)
        self.ssl = raw_conf.get('ssl', False) is True
        self.databases = raw_conf.get('databases', None)
        self.replica = raw_conf.get('replica', 1)
        self.template_loader = raw_conf.get('template_loader', 'system')
        self.auth_enabled = raw_conf.get('enable_auth') is True

        local_conf = raw_conf.get('local_conf', False)
        if local_conf is not False:
            if not local_conf.startswith('/'):
                local_conf = opj(self.directories['conf'], local_conf)
            local_conf = load_config(local_conf)
            self.__dict__.update(**local_conf)



    def __getitem__(self, item):
        return self.__getattribute__(item)
