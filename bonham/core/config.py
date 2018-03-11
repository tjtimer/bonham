"""

 config
"""
import os

from bonham.core.utils import opj


__all__ = ('load_config', 'get_config')

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
    root_directory = config.get('root_directory', os.getcwd())
    application = config.get('application_root','application')
    if not application.startswith('/'):
        application = opj(root_directory, application)
    public = config.get('public_root', 'public')
    if not public.startswith('/'):
        public = opj(root_directory, public)
    if config.get('template_loader', 'system') == 'system':
        templates = opj(application, 'templates')
    else:
        templates = 'templates'
    directories = dict(
        root=root_directory,
        application=application,
        public=public,
        templates=templates,
        certificates = opj(application, '.certificates'),
        secrets = opj(application, '.secrets'),
        sockets = opj(application, '.scks'),
        conf = opj(application, 'conf'),
        logs = opj(application, 'logs'),
        tmp = opj(application, 'tmp'),
        static = opj(public, config.get('static_dir', 'static')),
        media = opj(public, config.get('media_dir', 'media'))
    )
    return directories

def get_config(conf_path: str):
    _conf = load_config(conf_path)
    _next = parse_directories(_conf)
