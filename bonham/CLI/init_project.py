"""
init_project
"""
import os
import shutil
import socket

import arrow
from jinja2 import Template

from bonham.core.security import create_app_pw
from bonham.core.utils import opj


def run(name: str = None, restart: bool = False, config: dict = None):
    if config is None:
        config = {}
    if restart is False:
        print('Starting a new project is exciting, isn\'t it.')
        print('Let\'s get it on!')
    if name is None:
        print('What should be the name of your new project?')
        name = input()
    if os.path.isdir(name):
        bu_name = f'{name}_{arrow.now().format("YY_MM_DD")}_bu'
        print('there already is a folder with that name.')
        print(f'Should it be renamed to {bu_name}?')
        rename = input(f'rename [y|n]: ')
        if rename == 'y':
            shutil.move(name, bu_name)
        else:
            print('Okay, let\'s start again.')
            run(restart=True)
    config['name'] = name
    print('creating your projects root folder...')
    os.mkdir(name)
    current_dir = os.getcwd()
    config['root_dir'] = os.path.join(current_dir, name)
    os.chdir(config['root_dir'])
    print('creating a folder for your configuration files...')
    os.mkdir('conf')
    print('creating a folder for your log files...')
    os.mkdir('log')
    print('creating a folder for your apps...')
    os.mkdir('apps')
    print('creating a folder for your templates...')
    os.mkdir('templates')
    print('Do you wanna have the bonham auth system enabled?')
    e_a = input('enable auth [y|n]: ')
    config['enable_auth'] = 'on' if 'y' in e_a.lower() else 'off'
    print('Do you wanna use ssl?')
    ssl = input('enable ssl [y|n]: ')
    config['ssl'] = 'on' if 'y' in ssl.lower() else 'off'
    print('Do you wanna enable debug mode?')
    config['debug_env'] = socket.gethostname()
    config['require_pw'] = 'off'
    if input('Do you wanna create a password needed to start the app? [y|n]') == 'y':
        create_app_pw(config)
        config['require_pw'] = 'on'
    print('Writing your configuration file.')
    print('You will find it in your projects conf folder named app.conf.yaml.')
    templates_path = opj(os.path.dirname(__file__), 'templates')
    for filename in ['app.conf.yaml', 'logging.conf.yaml']:
        conf_template = opj(templates_path, filename)
        conf = opj(config['root_dir'], 'conf', filename)
        with open(conf_template, 'r') as tpl:
            template = Template(tpl.read())
            with open(conf, 'w') as cf:
                cf.write(template.render(**config))

    success_start = f"{f' It is done! ':^*80}"
    success_middle = f"{f' You can now take a break and enjoy this wonderful day. ':^-80}"
    success_end = f"{f' Bonham ':^*80}"
    print(f"""{success_start}\n{success_middle}\n{success_end}""")
